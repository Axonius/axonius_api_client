# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from . import exceptions

LOG = logging.getLogger(__name__)


class ApiClient(object):
    _API_VERSION = 1
    ''':obj:`int`: Version of the API this ApiClient is made for.'''

    _API_PATH = 'api/V{version}/'.format(version=_API_VERSION)
    ''':obj:`str`: Base path of API.'''

    def __init__(self, auth_client):
        self._log = LOG.getChild(self.__class__.__name__)
        ''':obj:`logging.Logger`: Logger for this object.'''

        if not auth_client.is_logged_in:
            raise exceptions.MustLogin(auth_client=auth_client)

        self._auth_client = auth_client
        ''':obj:`axonius_api_client.auth.AuthBase`: Authentication object.'''

    def _request(self, method, route, **kwargs):
        sargs = {}
        sargs.update(kwargs)
        sargs['route'] = route
        sargs['method'] = method
        sargs.setdefault('path', self._API_PATH)

        response = self._auth_client(**sargs)
        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            msg = 'Response for {path}/{route} is not JSON'
            msg = msg.format(**sargs)
            self._log.debug(msg)
            return response.text

    # def get_fields_device(self):
    #     return self._request(method='get', route='devices/fields', private=True)

    # def get_fields_user(self):
    #     return self._request(method='get', route='users/fields', private=True)

    def _get_devices(self, query=None, fields=None, row_start=0, row_count=50):
        params = {}
        params['skip'] = row_start
        params['limit'] = row_count

        if query:
            params['query'] = query

        if fields:
            params['fields'] = fields
        return self._request(method='get', route='devices', params=params)

    def get_devices(self, query=None, fields=None, page_size=0):
        print(self, 'TODO')
