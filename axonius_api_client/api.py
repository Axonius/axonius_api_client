# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from . import exceptions

LOG = logging.getLogger(__name__)
GENERIC_FIELD_PREFIX = 'specific_data.data.'
ADAPTER_FIELD_PREFIX = 'adapters_data.'


class ApiClient(object):
    _API_VERSION = 1
    ''':obj:`int`: Version of the API this ApiClient is made for.'''

    _API_PATH = 'api/V{version}/'.format(version=_API_VERSION)
    ''':obj:`str`: Base path of API.'''

    DEVICE_FIELDS = {'generic': ['hostname', 'name', 'network_interfaces.mac', 'network_interfaces.ips']}

    def __init__(self, auth):
        self._log = LOG.getChild(self.__class__.__name__)
        ''':obj:`logging.Logger`: Logger for this object.'''

        self._auth = auth
        ''':obj:`axonius_api_client.auth.AuthBase`: Authentication object.'''

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return '{c.__module__}.{c.__name__}(auth={auth})'.format(c=self.__class__, auth=self._auth)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    def _request(self, method, route, require_json=True, **kwargs):
        sargs = {}
        sargs.update(kwargs)
        sargs['route'] = route
        sargs['method'] = method
        sargs.setdefault('path', self._API_PATH)

        response = self._auth.http_client(**sargs)
        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            msg = 'Response from "{response.url}" is not JSON'
            msg = msg.format(response=response)

            if require_json:
                msg = '{msg} - response text:\n{text}'.format(msg=msg, text=response.text)
                raise exceptions.PackageError(msg)

            self._log.warning(msg)
            return response.text

    def get_device_fields(self):
        try:
            return self._request(method='get', route='devices/fields')
        except Exception:
            msg = 'Unable to get device fields from API'
            self._log.error(msg)
            return None

    def get_user_fields(self):
        try:
            return self._request(method='get', route='users/fields')
        except Exception:
            msg = 'Unable to get user fields from API'
            self._log.error(msg)
            return None

    def _get_devices(self, query=None, fields=None, row_start=0, page_size=50):
        params = {}
        params['skip'] = row_start
        params['limit'] = page_size

        if query:
            params['query'] = query

        if fields:
            if isinstance(fields, (list, tuple)):
                fields = ','.join(fields)
            params['fields'] = fields
        return self._request(method='get', route='devices', params=params)

    def _validate_device_fields(self, **fields):
        validated_fields = []
        device_fields = self.get_device_fields()

        for adapter_name, adapter_fields in fields:
            adapter_name = None if adapter_name in ['specific', 'general'] else adapter_name
            for adapter_field in adapter_fields:
                adapter_field = find_field(name=adapter_field, fields=device_fields, adapter_name=adapter_name)
                validated_fields.append(adapter_field)
        return validated_fields

    def get_devices(self, query=None, page_size=100, max_rows=0, **fields):
        for k, v in self.DEVICE_FIELDS:
            fields.setdefault(k, v)

        fields = self._validate_device_fields(**fields)

        page = self._get_devices(query=query, fields=fields, row_start=0, page_size=page_size)

        for device in page['assets']:
            yield device

        total = page['page']['totalResources']
        seen = len(page['assets'])

        while seen < total:
            page = self._get_devices(query=query, fields=fields, row_start=seen, page_size=page_size)

            if not page['assets']:
                break

            for device in page['assets']:
                yield device

            if max_rows and seen >= max_rows:
                break

            seen += len(page['assets'])


def find_adapter(name, known_names=None):
    postfix = '_adapter'
    name = name if name.endswith(postfix) else name + postfix

    if not known_names:
        return name

    if name in known_names:
        return known_names[known_names.index(name)]

    postfix_len = len(postfix)
    known_names = [x[:postfix_len] if x.endswith(postfix) else x for x in known_names]
    raise exceptions.UnknownAdapterName(name=name, known_names=known_names)


def find_field(name, fields=None, adapter_name=None):
    if adapter_name:
        known_adapter_names = fields['specific'] if fields else None
        adapter_name = find_adapter(name=adapter_name, known_names=known_adapter_names)
        prefix = ADAPTER_FIELD_PREFIX + adapter_name
        container = fields['specific'][adapter_name] if fields else None
    else:
        prefix = GENERIC_FIELD_PREFIX
        container = fields['generic'] if fields else None

    name = name if name.startswith(prefix) else prefix + name

    if not container:
        return name

    known_names = [x['name'] for x in container]

    if name in known_names:
        return known_names[known_names.index(name)]

    prefix_len = len(prefix)
    known_names = [x[prefix_len:] if x.startswith(prefix) else x for x in known_names]
    raise exceptions.UnknownFieldName(name=name, known_names=known_names, adapter_name=adapter_name)
