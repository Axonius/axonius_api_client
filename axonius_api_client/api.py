# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from . import exceptions

LOG = logging.getLogger(__name__)

GENERIC_FIELD_PREFIX = "specific_data.data."
""":obj:`str`: Prefix that all generic fields should begin with."""

ADAPTER_FIELD_PREFIX = "adapters_data.{adapter}."
""":obj:`str`: Prefix that all adapter fields should begin with."""


class ApiClient(object):
    """API client for Axonius REST API."""

    _API_VERSION = 1
    """:obj:`int`: Version of the API this ApiClient is made for."""

    _API_PATH = "api/V{version}/".format(version=_API_VERSION)
    """:obj:`str`: Base path of API."""

    DEFAULT_DEVICE_FIELDS = {
        "generic": ["hostname", "network_interfaces.mac", "network_interfaces.ips"]
    }

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

    def get_device_saved_queries(self, query=None, page_size=20, max_rows=0):
        """Pass."""
        page = self._get_saved_queries(query=query, page_size=page_size, row_start=0)

        for row in page["assets"]:
            yield row

        seen = len(page["assets"])

        # totalResources on page for this call just shows page_size
        while True:
            page = self._get_saved_queries(
                query=query, page_size=page_size, row_start=seen
            )

            for row in page["assets"]:
                yield row

            if (max_rows and seen >= max_rows) or not page["assets"]:
                break

            seen += len(page["assets"])

    def get_device_saved_queries_by_name(
        self, name, regex=True, page_size=20, max_rows=0
    ):
        """Pass."""
        if regex:
            query = 'name == regex("{}", "i")'.format(name)
        else:
            query = 'name == "{}"'.format(name)

        found = list(
            self.get_saved_queries(query=query, page_size=page_size, max_rows=max_rows)
        )
        if not found:
            raise exceptions.SavedQueryNotFound(query=query)
        return found

    def get_device_fields(self):
        """Get the fields available for devices.

        Notes:
            Will only return fields on Axonius v2.7 or greater. Caches result to self.

        Returns:
            :obj:`dict`

        """
        self._device_fields = getattr(
            self, "_device_fields", self._request(method="get", route="devices/fields")
        )
        return self._device_fields

    def get_device_count(self, query=None):
        """Get the number of devices for a given query.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI to count devices of.

        Returns:
            :obj:`int`

        """
        params = {}
        if query:
            params["filter"] = query
        return self._request(method="get", route="devices/count", params=params)

    def get_device_by_id(self, id):
        """Get a device by internal_axon_id.

        Args:
            id (:obj:`str`):
                internal_axon_id of device to get.

        Raises:
            :exc:`exceptions.DeviceIDNotFound`:
                When :meth:`_request` raises exception.

        Returns:
            :obj:`dict`

        """
        try:
            return self._request(method="get", route="devices/{id}".format(id=id))
        except Exception:
            raise exceptions.DeviceIDNotFound(id=id)

    def get_devices(self, query=None, page_size=100, max_rows=0, **fields):
        """Get devices for a given query using paging.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI to select devices to return.

                Defaults to: None.
            page_size (:obj:`int`, optional):
                Get N devices per page.

                Defaults to: 100.
            max_rows (:obj:`int`, optional):
                If not 0, only return up to N devices.

                Defaults to: 0.
            **fields: Fields to include in result.
                * generic=['f1', 'f2'] for generic fields.
                * adapter=['f1', 'f2'] for adapter specific fields.

        Notes:
            Fields will be updated with :attr:`DEFAULT_DEVICE_FIELDS`.

        Yields:
            :obj:`dict`: each row found in 'assets' from return.

        """
        for k, v in self.DEFAULT_DEVICE_FIELDS.items():
            fields.setdefault(k, v)

        device_fields = self.get_device_fields()
        fields = self._validate_fields(known_fields=device_fields, **fields)

        page = self._get_devices(
            query=query, fields=fields, row_start=0, page_size=page_size
        )

        for row in page["assets"]:
            yield row

        total = page["page"]["totalResources"]
        seen = len(page["assets"])

        while seen < total:
            page = self._get_devices(
                query=query, fields=fields, row_start=seen, page_size=page_size
            )

            for row in page["assets"]:
                yield row

            if (max_rows and seen >= max_rows) or not page["assets"]:
                break

            seen += len(page["assets"])

    def get_user_fields(self):
        """Get the fields available for users.

        Notes:
            Will only return fields on Axonius v2.7 or greater. Caches result to self.

        Returns:
            :obj:`dict`

        """
        self._user_fields = getattr(
            self, "_user_fields", self._request(method="get", route="users/fields")
        )
        return self._user_fields

    def _request(self, route, method="get", raw=False, **kwargs):
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
            **kwargs:
                Passed to :meth:`axonius_api_client.http.HttpClient.__call__`

        """
        sargs = {}
        sargs.update(kwargs)
        sargs["route"] = route
        sargs["method"] = method
        sargs.setdefault("path", self._API_PATH)

        response = self._auth.http_client(**sargs)
        response.raise_for_status()

        return response if raw else response.json()

    def _get_devices(self, query=None, fields=None, row_start=0, page_size=100):
        """Get a page of devices for a given query.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI to select devices to return.

                Defaults to: None.
            fields (:obj:`list` of :obj:`str` or :obj:`str`):
                List of device fields to include in return.
                If str, CSV seperated list of fields.
                If list, strs of fields.

                Defaults to: None.
            row_start (:obj:`int`, optional):
                Skip N devices in the return.

                Defaults to: 0.
            page_size (:obj:`int`, optional):
                Include N devices in the return.

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
        return self._request(method="get", route="devices", params=params)

    def _validate_fields(self, known_fields, **fields):
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
            for field in afields:
                field = find_field(name=field, fields=known_fields, adapter=name)
                if field not in validated_fields:
                    validated_fields.append(field)

        return validated_fields

    def _get_device_saved_queries(self, query=None, row_start=0, page_size=0):
        """Pass."""
        params = {}

        if page_size:
            params["limit"] = page_size

        if row_start:
            params["skip"] = row_start

        if query:
            params["filter"] = query

        return self._request(method="get", route="devices/views", params=params)


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

    if not name.startswith(prefix):
        name = prefix + name

    if not container:
        return name

    known_names = [x["name"] for x in container]

    if name in known_names:
        return known_names[known_names.index(name)]

    prefix_len = len(prefix)
    known_names = [x[prefix_len:] if x.startswith(prefix) else x for x in known_names]
    raise exceptions.UnknownFieldName(
        name=name, known_names=known_names, adapter=adapter
    )
