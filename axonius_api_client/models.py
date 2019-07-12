# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging

import six

from . import constants
from . import exceptions
from . import tools

LOG = logging.getLogger(__name__)

GENERIC_FIELD_PREFIX = "specific_data.data"
""":obj:`str`: Prefix that all generic fields should begin with."""

ADAPTER_FIELD_PREFIX = "adapters_data.{adapter}"
""":obj:`str`: Prefix that all adapter fields should begin with."""


class ApiVersion1(object):
    """Mixin for API version 1."""

    @property
    def _api_version(self):
        """Get the API version to use.

        Returns:
            :obj:`int`

        """
        return 1

    @property
    def _api_path(self):
        """Get the API path to use.

        Returns:
            :obj:`str`

        """
        return "api/V{version}/".format(version=self._api_version)


@six.add_metaclass(abc.ABCMeta)
class ApiBase(object):
    """API client for Axonius REST API."""

    def __init__(self, auth):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.auth.AuthBase`):
                Authentication object.

        """
        self._log = LOG.getChild(self.__class__.__name__)
        """:obj:`logging.Logger`: Logger for this object."""

        self._auth = auth
        """:obj:`axonius_api_client.auth.AuthBase`: Authentication object."""

        if not auth.is_logged_in:
            raise exceptions.NotLoggedIn(auth=auth)

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return "{c.__module__}.{c.__name__}(auth={auth})".format(
            c=self.__class__, auth=self._auth
        )

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    def _request(self, route, method="get", raw=False, do_raise=True, **kwargs):
        """Perform a REST API request.

        Args:
            route (:obj:`str`):
                REST API route to request.
            method (:obj:`str`, optional):
                HTTP method to use in request.

                Defaults to: "get".
            raw (:obj:`bool`, optional):
                Return the raw response. If False, return response.json().

                Defaults to: False.
            do_raise (:obj:`bool`, optional):
                Call :meth:`requests.Response.raise_for_status`.

                Defaults to: True.
            **kwargs:
                Passed to :meth:`axonius_api_client.http.HttpClient.__call__`

        """
        obj_route = kwargs.pop("obj_route", self._obj_route)

        sargs = {}
        sargs.update(kwargs)

        if route:
            sargs["route"] = tools.urljoin(obj_route, route)
        else:
            sargs["route"] = obj_route

        sargs["method"] = method

        sargs.setdefault("path", self._api_path)

        response = self._auth.http_client(**sargs)
        if do_raise:
            try:
                response.raise_for_status()
            except Exception as exc:
                raise exceptions.ResponseError(response=response, exc=exc)

        return response if raw else response.json()

    @abc.abstractproperty
    def _api_version(self):
        """Get the API version to use.

        Returns:
            :obj:`int`

        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def _api_path(self):
        """Get the API path to use.

        Returns:
            :obj:`str`

        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def _obj_route(self):
        """Get the object route.

        Returns:
            :obj:`str`

        """
        raise NotImplementedError  # pragma: no cover


@six.add_metaclass(abc.ABCMeta)
class UserDeviceBase(object):
    """Mixins for User & Device models."""

    def get_fields(self):
        """Get the fields.

        Notes:
            Will only return fields on Axonius v2.7 or greater. Caches result to self.

        Returns:
            :obj:`dict`

        """
        if not getattr(self, "_fields", None):
            self._fields = self._request(method="get", route="fields")
        return self._fields

    def get_labels(self):
        """Get the labels.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return self._request(method="get", route="labels")

    def add_labels_by_rows(self, rows, labels):
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
            response = self._add_labels(labels=labels, ids=group)
            processed += response

        return processed

    def add_labels_by_query(self, query, labels):
        """Add labels to objects using a query to select objects.

        Args:
            query (:obj:`str`):
                Query built from Query Wizard in GUI to select objects to add labels to.
            labels (:obj:`list` of `str`):
                Labels to add to rows returned from query.

        Returns:
            :obj:`int`: Number of objects that had labels added

        """
        rows = list(self.get(query=query, default_fields=False))
        return self.add_labels_by_rows(rows=rows, labels=labels)

    def delete_labels_by_rows(self, rows, labels):
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
            response = self._delete_labels(labels=labels, ids=group)
            processed += response

        return processed

    def delete_labels_by_query(self, query, labels):
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
        rows = list(self.get(query=query, default_fields=False))
        return self.delete_labels_by_rows(rows=rows, labels=labels)

    def create_saved_query(
        self,
        name,
        query,
        page_size=constants.DEFAULT_PAGE_SIZE,
        sort_field="",
        sort_descending=True,
        sort_adapter="generic",
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

                Defaults to: :data:`constants.DEFAULT_PAGE_SIZE`.
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
        tools.check_max_page_size(page_size=page_size)
        for k, v in self._default_fields.items():
            fields.setdefault(k, v)

        known_fields = self.get_fields()
        validated_fields = validate_fields(known_fields=known_fields, **fields)

        if sort_field:
            sort_field = find_field(
                name=sort_field, fields=known_fields, adapter=sort_adapter
            )

        data = {}
        data["name"] = name
        data["query_type"] = "saved"
        data["view"] = {}
        data["view"]["fields"] = validated_fields

        # FUTURE: find out what this is
        data["view"]["historical"] = None

        # FUTURE: find out if this only impacts GUI
        data["view"]["columnSizes"] = []

        # FUTURE: find out if this only impacts GUI
        data["view"]["page"] = 0

        # FUTURE: find out if this only impacts GUI
        data["view"]["pageSize"] = page_size

        data["view"]["query"] = {}

        # FUTURE: validate 'expressions' is not needed
        # data["view"]["query"]["expressions"] = []

        data["view"]["query"]["filter"] = query
        data["view"]["sort"] = {}
        data["view"]["sort"]["desc"] = sort_descending
        data["view"]["sort"]["field"] = sort_field

        return self._request(method="post", route="views", json=data)

    def delete_saved_query_by_name(self, name, regex=False, only1=True):
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
        found = self.get_saved_query_by_name(name=name, regex=regex, only1=True)
        ids = [x["uuid"] for x in found] if isinstance(found, list) else [found["uuid"]]
        return self._delete_saved_query(ids=ids)

    def get_saved_query(
        self, query=None, page_size=constants.DEFAULT_PAGE_SIZE, max_rows=0
    ):
        """Get saved queries using paging.

        Args:
            query (:obj:`str`, optional):
                Query to filter rows to return. This is NOT a query built by
                the Query Wizard in the GUI. This is something else. See
                :meth:`get_user_saved_query_by_name` for an example query.

                Defaults to: None.
            page_size (:obj:`int`, optional):
                Get N rows per page.

                Defaults to: :data:`constants.DEFAULT_PAGE_SIZE`.
            max_rows (:obj:`int`, optional):
                If not 0, only return up to N rows.

                Defaults to: 0.

        Yields:
            :obj:`dict`: Each row found in 'assets' from return.

        """
        tools.check_max_page_size(page_size=page_size)
        page = self._get_saved_query(query=query, page_size=page_size, row_start=0)

        for row in page["assets"]:
            yield row

        seen = len(page["assets"])

        while True:
            page = self._get_saved_query(
                query=query, page_size=page_size, row_start=seen
            )

            for row in page["assets"]:
                yield row

            if (max_rows and seen >= max_rows) or not page["assets"]:
                break

            seen += len(page["assets"])

    def get_saved_query_by_name(self, name, regex=True, only1=False):
        """Get saved queries by name using paging.

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
        if regex:
            query = 'name == regex("{name}", "i")'.format(name=name)
        else:
            query = 'name == "{name}"'.format(name=name)

        found = list(self.get_saved_query(query=query))

        if not found or (len(found) > 1 and only1):
            raise exceptions.ObjectNotFound(
                value=query, value_type="query", object_type="Saved Query"
            )

        return found[0] if only1 else found

    def get_count(self, query=None):
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
        return self._request(method="get", route="count", params=params)

    def get(
        self,
        query=None,
        page_size=constants.DEFAULT_PAGE_SIZE,
        max_rows=0,
        default_fields=True,
        **fields
    ):
        """Get objects for a given query using paging.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI to select rows to return.

                Defaults to: None.
            page_size (:obj:`int`, optional):
                Get N rows per page.

                Defaults to: :data:`constants.DEFAULT_PAGE_SIZE`.
            max_rows (:obj:`int`, optional):
                If not 0, only return up to N rows.

                Defaults to: 0.
            default_fields (:obj:`bool`, optional):
                Update **fields with :attr:`_default_fields` if no fields supplied.

                Defaults to: True.
            **fields: Fields to include in result.
                * generic=['f1', 'f2'] for generic fields.
                * adapter=['f1', 'f2'] for adapter specific fields.

        Yields:
            :obj:`dict`: each row found in 'assets' from return.

        """
        if not fields and default_fields:
            for k, v in self._default_fields.items():
                fields.setdefault(k, v)

        known_fields = self.get_fields()
        validated_fields = validate_fields(known_fields=known_fields, **fields)
        print(validated_fields)

        page = self._get(
            query=query, fields=validated_fields, row_start=0, page_size=page_size
        )

        seen = 0

        for row in page["assets"]:
            if max_rows and seen >= max_rows:
                return
            seen += 1
            yield row

        while True:
            if (max_rows and seen >= max_rows) or not page["assets"]:
                return

            page = self._get(
                query=query,
                fields=validated_fields,
                row_start=seen,
                page_size=page_size,
            )

            for row in page["assets"]:
                seen += 1
                yield row

    def get_by_id(self, id):
        """Get an object by internal_axon_id.

        Args:
           id (:obj:`str`):
               internal_axon_id of object to get.

        Raises:
           :exc:`exceptions.ObjectNotFound`:
               When :meth:`_request` raises exception.

        Returns:
           :obj:`dict`

        """
        try:
            return self._request(method="get", route="{id}".format(id=id))
        except Exception:
            raise exceptions.ObjectNotFound(
                value=id, value_type="Axonius ID", object_type=self._obj_route
            )

    def get_by_name(self, name, regex=False, only1=True, **kwargs):
        """Get objects by name using paging.

        Args:
            name (:obj:`int`):
                Name to match using :attr:`_name_field`.
            **kwargs: Passed thru to :meth:`get`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        if regex:
            query = '{field} == regex("{name}", "i")'
        else:
            query = '{field} == "{name}"'

        query = query.format(field=self._name_field, name=name)

        kwargs["query"] = query

        found = list(self.get(**kwargs))

        if not found or (len(found) > 1 and only1):
            raise exceptions.ObjectNotFound(
                value=query, value_type="query", object_type=self._obj_route
            )

        return found[0] if only1 else found

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
        return self._request(method="get", route="", params=params)

    def _get_saved_query(self, query=None, row_start=0, page_size=0):
        """Get device saved queries.

        Args:
            query (:obj:`str`, optional):
                Query to filter rows to return. This is NOT a query built by
                the Query Wizard in the GUI. This is something else. See
                :meth:`get_user_saved_query_by_name` for an example query. Empty
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
        params = {}

        if page_size:
            params["limit"] = page_size

        if row_start:
            params["skip"] = row_start

        if query:
            params["filter"] = query

        return self._request(method="get", route="views", params=params)

    def _delete_saved_query(self, ids):
        """Delete saved queries by ids.

        Args:
            ids (:obj:`list` of :obj:`str`):
                List of UUID's of saved queries to delete.

        Returns:
            :obj:`str`: empty string

        """
        data = {"ids": ids}
        return self._request(method="delete", route="views", json=data)

    def _add_labels(self, labels, ids, query=None):
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
        return self._request(method="post", route="labels", json=data)

    def _delete_labels(self, labels, ids, query=None):
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
        return self._request(method="delete", route="labels", json=data)

    @abc.abstractproperty
    def _name_field(self):
        """Get the field to use in :meth:`get_by_name`.

        Returns:
            :obj:`str`

        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def _default_fields(self):
        """Fields to set as default for methods with **fields.

        Returns:
            :obj:`dict`

        """
        raise NotImplementedError  # pragma: no cover


def find_adapter(name, known_names=None):
    """Find an adapter by name.

    Args:
        name (:obj:`str`):
            Name of adapter to find.
        known_names (:obj:`list` of :obj:`str`, optional):
            List of known adapter names.

            Defaults to: None.

    Notes:
        If known_names is None, this will just ensure name ends with '_adapter'.

    Raises:
        :exc:`exceptions.UnknownAdapterName`: If name can not be found in known_names.

    Returns:
        :obj:`str`

    """
    postfix = "_adapter"
    name = name if name.endswith(postfix) else name + postfix

    if not known_names:
        return name

    if name in known_names:
        return known_names[known_names.index(name)]

    postfix_len = len(postfix)
    known_names = [x[:-postfix_len] if x.endswith(postfix) else x for x in known_names]
    raise exceptions.UnknownAdapterName(name=name, known_names=known_names)


def find_field(name, adapter, fields=None):
    """Find a field for a given adapter.

    Args:
        name (:obj:`str`):
            Name of field to find.
        adapter (:obj:`str`):
            Name of adapter to look for field in.
            If 'generic' look for the field in generic fields.
        fields (:obj:`dict`, optional):
            Return from :meth:`ApiClient.get_device_fields`.

            Defaults to: None.

    Notes:
        If adapter 'generic', ensure name begins with :attr:`GENERIC_FIELD_PREFIX`,
        otherwise ensure name begins with :attr:`ADAPTER_FIELD_PREFIX`.

        If fields is None, we can't validate that the field exists, so we just ensure
        the name is fully qualified.

        If name in "all" or prefix, returns prefix.

    Raises:
        :exc:`exceptions.UnknownFieldName`:
            If fields is not None and name can not be found in fields.

    Returns:
        :obj:`str`

    """
    if adapter == "generic":
        prefix = GENERIC_FIELD_PREFIX
        container = fields["generic"] if fields else None
    else:
        known_adapters = list(fields["specific"].keys()) if fields else None
        adapter = find_adapter(name=adapter, known_names=known_adapters)
        prefix = ADAPTER_FIELD_PREFIX.format(adapter=adapter)
        container = fields["specific"][adapter] if fields else None

    if not name.startswith(prefix):
        fq_name = ".".join([x for x in [prefix, name] if x])
    else:
        fq_name = name

    if not container:
        return name if name in ["adapters", "labels"] else fq_name

    known_names = [x["name"] for x in container]

    for check in [name, fq_name]:
        if check in ["all", prefix]:
            return prefix
        if check in known_names:
            return known_names[known_names.index(check)]

    prefix = prefix + "."
    prefix_len = len(prefix + ".")
    known_names = [x[prefix_len:] if x.startswith(prefix) else x for x in known_names]
    known_names += ["all", prefix]
    raise exceptions.UnknownFieldName(
        name=name, known_names=known_names, adapter=adapter
    )


def validate_fields(known_fields, **fields):
    """Validate provided fields are valid.

    Args:
        known_fields (:obj:`dict`):
            Known fields from :meth:`get_device_fields` or :meth:`get_user_fields`.
        **fields: Fields to validate.
            * generic=['f1', 'f2'] for generic fields.
            * adapter=['f1', 'f2'] for adapter specific fields.

    Notes:
        This will try to use :meth:`get_device_fields` to validate the device
        fields, but if it returns None it will just ensure the fields are
        fully qualified.

        * generic=['field1'] => ['specific_data.data.field1']
        * adapter=['field1'] =>['adapters_data.adapter_name.field1']

    Returns:
        :obj:`list` of :obj:`str`

    """
    validated_fields = []

    for name, afields in fields.items():
        if not isinstance(afields, (tuple, list)):
            continue
        for field in afields:
            field = find_field(name=field, fields=known_fields, adapter=name)
            if field not in validated_fields:
                validated_fields.append(field)

    return validated_fields


@six.add_metaclass(abc.ABCMeta)
class AuthBase(object):
    """Abstract base class for all Authentication methods."""

    @abc.abstractproperty
    def _api_version(self):
        """Get the API version to use.

        Returns:
            :obj:`int`

        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def _api_path(self):
        """Get the API path to use.

        Returns:
            :obj:`str`

        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def login(self):
        """Login to API."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def logout(self):
        """Logout from API."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def http_client(self):
        """Get HttpClient object.

        Returns:
            :obj:`axonius_api_client.http.HttpClient`

        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def is_logged_in(self):
        """Check if login has been called.

        Returns:
            :obj:`bool`

        """
        raise NotImplementedError  # pragma: no cover


class AuthMixins(object):
    """Mixins for AuthBase."""

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        bits = [
            "url={!r}".format(self.http_client.url),
            "is_logged_in={}".format(self.is_logged_in),
        ]
        bits = "({})".format(", ".join(bits))
        return "{c.__module__}.{c.__name__}{bits}".format(c=self.__class__, bits=bits)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @property
    def http_client(self):
        """Get HttpClient object.

        Returns:
            :obj:`axonius_api_client.http.HttpClient`

        """
        return self._http_client

    def _check_http_lock(self):
        """Check HTTP client not already used by another Auth.

        Raises:
            :exc:`exceptions.PackageError`

        """
        auth_lock = getattr(self.http_client, "_auth_lock", None)
        if auth_lock:
            msg = "{http_client} already being used by {auth}"
            msg = msg.format(http_client=self.http_client, auth=auth_lock)
            raise exceptions.PackageError(msg)

    def _set_http_lock(self):
        """Set HTTP Client auth lock."""
        self._http_client._auth_lock = self

    def validate(self):
        """Validate credentials.

        Raises:
            :exc:`exceptions.InvalidCredentials`

        """
        if not self.is_logged_in:
            raise exceptions.NotLoggedIn(auth=self)

        response = self.http_client(
            method="get", path=self._api_path, route="devices/count"
        )

        if response.status_code in [401, 403]:
            raise exceptions.InvalidCredentials(auth=self, exc=None)

        try:
            response.raise_for_status()
        except Exception as exc:
            raise exceptions.InvalidCredentials(auth=self, exc=exc)

    def logout(self):
        """Logout from API."""
        if not self.is_logged_in:
            raise exceptions.NotLoggedIn(auth=self)
        self._logout()
