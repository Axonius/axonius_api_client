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

ADAPTER_FIELD_PREFIX = "adapters_data.{adapter_name}."
""":obj:`str`: Prefix that all adapter fields should begin with."""


class ApiClient(object):
    """API client for Axonius REST API."""

    _API_VERSION = 1
    """:obj:`int`: Version of the API this ApiClient is made for."""

    _API_PATH = "api/V{version}/".format(version=_API_VERSION)
    """:obj:`str`: Base path of API."""

    DEVICE_FIELDS = {
        "generic": [
            "hostname",
            "name",
            "network_interfaces.mac",
            "network_interfaces.ips",
        ]
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

    def get_device_fields(self):
        """Get the fields available for devices.

        Notes:
            Will only return fields on Axonius v2.7 or greater.

        Returns:
            :obj:`dict`

        """
        try:
            return self._request(method="get", route="devices/fields")
        except Exception:
            msg = "Unable to get device fields from API"
            self._log.error(msg)
            return None

    def get_user_fields(self):
        """Get the fields available for users.

        Notes:
            Will only return fields on Axonius v2.7 or greater.

        Returns:
            :obj:`dict`

        """
        try:
            return self._request(method="get", route="users/fields")
        except Exception:
            msg = "Unable to get user fields from API"
            self._log.error(msg)
            return None

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
        """
        params = {}
        params["skip"] = row_start
        params["limit"] = page_size

        if query:
            params["query"] = query

        if fields:
            if isinstance(fields, (list, tuple)):
                fields = ",".join(fields)
            params["fields"] = fields
        return self._request(method="get", route="devices", params=params)

    def _validate_device_fields(self, **fields):
        """Validate provided fields are valid.

        Args:
            **fields: Fields to validate.

                * 'generic' = ['f1', 'f2'] for generic data fields.
                * 'specific' = ['f1', 'f2'] for generic data fields.
                * 'adapter_name' = ['f1', 'f2'] for adapter specific data fields.

        Notes:
            This will try to use :meth:`get_device_fields` to validate the device
            fields, but if it returns None it will just ensure the fields are
            fully qualified.

            * 'generic': ['field1'] => ['specific_data.data.field1']
            * 'adapter_name': ['field1'] =>['adapters_data.adapter_name.field1']

        """
        validated_fields = []
        device_fields = self.get_device_fields()

        for adapter_name, adapter_fields in fields:
            adapter_name = (
                None if adapter_name in ["specific", "general"] else adapter_name
            )
            for adapter_field in adapter_fields:
                adapter_field = find_field(
                    name=adapter_field, fields=device_fields, adapter_name=adapter_name
                )
                validated_fields.append(adapter_field)
        return validated_fields

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
                * 'generic' = ['f1', 'f2'] for generic data fields.
                * 'specific' = ['f1', 'f2'] for generic data fields.
                * 'adapter_name' = ['f1', 'f2'] for adapter specific data fields.

        """
        for k, v in self.DEVICE_FIELDS:
            fields.setdefault(k, v)

        fields = self._validate_device_fields(**fields)

        page = self._get_devices(
            query=query, fields=fields, row_start=0, page_size=page_size
        )

        for device in page["assets"]:
            yield device

        total = page["page"]["totalResources"]
        seen = len(page["assets"])

        while seen < total:
            page = self._get_devices(
                query=query, fields=fields, row_start=seen, page_size=page_size
            )

            if not page["assets"]:
                break

            for device in page["assets"]:
                yield device

            if max_rows and seen >= max_rows:
                break

            seen += len(page["assets"])


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
    known_names = [x[:postfix_len] if x.endswith(postfix) else x for x in known_names]
    raise exceptions.UnknownAdapterName(name=name, known_names=known_names)


def find_field(name, fields=None, adapter_name=None):
    """Find a field for a given adapter.

    Args:
        name (:obj:`str`):
            Name of field to find.
        fields (:obj:`dict`, optional):
            Return from :meth:`ApiClient.get_device_fields`.

            Defaults to: None.
        adapter_name (:obj:`str`, optional):
            Name of adapter to look for field in. If None, look for the field in the
            generic fields.

            Defaults to: None.

    Notes:
        If fields is None:
            * If adapter_name, ensure name begins with :attr:`ADAPTER_FIELD_PREFIX`.
            * If not adapter_name, ensure name begins with :attr:`GENERIC_FIELD_PREFIX`.

    Raises:
        :exc:`exceptions.UnknownFieldName`: If name can not be found in fields.

    Returns:
        :obj:`str`

    """
    if adapter_name:
        known_adapter_names = fields["specific"] if fields else None
        adapter_name = find_adapter(name=adapter_name, known_names=known_adapter_names)
        prefix = ADAPTER_FIELD_PREFIX.format(adapter_name=adapter_name)
        container = fields["specific"][adapter_name] if fields else None
    else:
        prefix = GENERIC_FIELD_PREFIX
        container = fields["generic"] if fields else None

    name = name if name.startswith(prefix) else prefix + name

    if not container:
        return name

    known_names = [x["name"] for x in container]

    if name in known_names:
        return known_names[known_names.index(name)]

    prefix_len = len(prefix)
    known_names = [x[prefix_len:] if x.startswith(prefix) else x for x in known_names]
    raise exceptions.UnknownFieldName(
        name=name, known_names=known_names, adapter_name=adapter_name
    )
