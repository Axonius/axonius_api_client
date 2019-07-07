# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging

import six

from . import exceptions
from . import tools

LOG = logging.getLogger(__name__)

GENERIC_FIELD_PREFIX = "specific_data.data."
""":obj:`str`: Prefix that all generic fields should begin with."""

ADAPTER_FIELD_PREFIX = "adapters_data.{adapter}."
""":obj:`str`: Prefix that all adapter fields should begin with."""


@six.add_metaclass(abc.ABCMeta)
class ApiClient(object):
    """API client for Axonius REST API."""

    @abc.abstractproperty
    def _obj_route(self):
        """Get the object route."""
        raise NotImplementedError  # pragma: no cover

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
        sargs = {}
        sargs.update(kwargs)
        if route:
            sargs["route"] = tools.urljoin(self._obj_route, route)
        else:
            sargs["route"] = self._obj_route
        sargs["method"] = method
        sargs.setdefault("path", self._API_PATH)

        response = self._auth.http_client(**sargs)
        if do_raise:
            try:
                response.raise_for_status()
            except Exception as exc:
                raise exceptions.ResponseError(response=response, exc=exc)

        return response if raw else response.json()


class ObjectMixins(object):
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

    def create_saved_query(
        self,
        name,
        query,
        page_size=25,
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
        for k, v in self.DEFAULT_FIELDS.items():
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

    def get_saved_query(self, query=None, page_size=20, max_rows=0):
        """Get saved queries using paging.

        Args:
            query (:obj:`str`, optional):
                Query to filter rows to return. This is NOT a query built by
                the Query Wizard in the GUI. This is something else. See
                :meth:`get_user_saved_query_by_name` for an example query.

                Defaults to: None.
            page_size (:obj:`int`, optional):
                Get N rows per page.

                Defaults to: 20.
            max_rows (:obj:`int`, optional):
                If not 0, only return up to N rows.

                Defaults to: 0.

        Yields:
            :obj:`dict`: each row found in 'assets' from return.

        """
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

    def get(self, query=None, page_size=100, max_rows=0, **fields):
        """Get objects for a given query using paging.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI to select rows to return.

                Defaults to: None.
            page_size (:obj:`int`, optional):
                Get N rows per page.

                Defaults to: 100.
            max_rows (:obj:`int`, optional):
                If not 0, only return up to N rows.

                Defaults to: 0.
            **fields: Fields to include in result.
                * generic=['f1', 'f2'] for generic fields.
                * adapter=['f1', 'f2'] for adapter specific fields.

        Notes:
            Fields will be updated with :attr:`DEFAULT_FIELDS`.

        Yields:
            :obj:`dict`: each row found in 'assets' from return.

        """
        for k, v in self.DEFAULT_FIELDS.items():
            fields.setdefault(k, v)

        known_fields = self.get_fields()
        validated_fields = validate_fields(known_fields=known_fields, **fields)

        page = self._get(
            query=query, fields=validated_fields, row_start=0, page_size=page_size
        )

        for row in page["assets"]:
            yield row

        total = page["page"]["totalResources"]
        seen = len(page["assets"])

        while seen < total:
            page = self._get(
                query=query,
                fields=validated_fields,
                row_start=seen,
                page_size=page_size,
            )

            for row in page["assets"]:
                yield row

            if (max_rows and seen >= max_rows) or not page["assets"]:
                break

            seen += len(page["assets"])

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

    def _get(self, query=None, fields=None, row_start=0, page_size=100):
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
                Skip N rows in the return.

                Defaults to: 0.
            page_size (:obj:`int`, optional):
                Include N rows in the return.

                Defaults to: 100.

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
                query will return all saved queries.

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


class ApiUsers(ApiClient, ObjectMixins):
    """User related API methods."""

    _API_VERSION = 1
    """:obj:`int`: Version of the API this ApiClient is made for."""

    _API_PATH = "api/V{version}/".format(version=_API_VERSION)
    """:obj:`str`: Base path of API."""

    DEFAULT_FIELDS = {
        "generic": [
            "adapters",
            "labels",
            "specific_data.data.username",
            "specific_data.data.last_seen",
        ]
    }
    """:obj:`dict`: Fields to set as default for methods with **fields."""

    @property
    def _obj_route(self):
        """Get the object route."""
        return "users"


class ApiDevices(ApiClient, ObjectMixins):
    """Device related API methods."""

    _API_VERSION = 1
    """:obj:`int`: Version of the API this ApiClient is made for."""

    _API_PATH = "api/V{version}/".format(version=_API_VERSION)
    """:obj:`str`: Base path of API."""

    DEFAULT_FIELDS = {
        "generic": [
            "adapters",
            "labels",
            "specific_data.data.hostname",
            "specific_data.data.network_interfaces.ips",
            "specific_data.data.last_seen",
        ]
    }
    """:obj:`dict`: Fields to set as default for methods with **fields."""

    @property
    def _obj_route(self):
        """Get the object route."""
        return "devices"


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

    fq_name = prefix + name if not name.startswith(prefix) else name

    if not container:
        return name if name in ["adapters", "labels"] else fq_name

    known_names = [x["name"] for x in container]

    if name in known_names:
        return known_names[known_names.index(name)]

    if fq_name in known_names:
        return known_names[known_names.index(fq_name)]

    prefix_len = len(prefix)
    known_names = [x[prefix_len:] if x.startswith(prefix) else x for x in known_names]
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
