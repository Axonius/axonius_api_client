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

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class AuthBase(object):
    @abc.abstractmethod
    def login(self):
        raise NotImplementedError

    @abc.abstractmethod
    def logout(self):
        raise NotImplementedError

    @abc.abstractmethod
    def validate(self):
        raise NotImplementedError

    @abc.abstractproperty
    def is_logged_in(self):
        raise NotImplementedError

    @abc.abstractproperty
    def http_client(self):
        raise NotImplementedError


class AuthMixins(object):
    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        bits = ['url={!r}'.format(self._http_client.url), 'is_logged_in={!r}'.format(self.is_logged_in)]
        bits = '({})'.format(', '.join(bits))
        return '{c.__module__}.{c.__name__}{bits}'.format(c=self.__class__, bits=bits)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    def validate(self):
        response = self._http_client(method='get', path=self._API_PATH, route='devices/count')

        if response.status_code in [401, 403]:
            msg = 'Login failed!'
            raise exceptions.InvalidCredentials(msg)

        response.raise_for_status()

    def logout(self):
        self._http_client.session.cookies.clear()
        self._http_client.session.headers.pop('api-key', None)
        self._http_client.session.headers.pop('api-secret', None)
        self._http_client.session.auth = None

    @property
    def http_client(self):
        return self._http_client


class AuthUser(AuthMixins, AuthBase):
    _API_VERSION = 1
    ''':obj:`int`: Version of the API this ApiClient is made for.'''

    _API_PATH = 'api/V{version}/'.format(version=_API_VERSION)
    ''':obj:`str`: Base path of API.'''

    def __init__(self, http_client, username, password):
        self._log = LOG.getChild(self.__class__.__name__)
        ''':obj:`logging.Logger`: Logger for this object.'''

        self._http_client = http_client
        ''':obj:`axonius_api_client.http.HttpClient`: HTTP Client.'''

        self._creds = {'username': username, 'password': password}
        ''':obj:`dict`: Credential store.'''

        self.login()

    def login(self):
        self.logout()

        self.http_client.session.auth = (self._creds['username'], self._creds['password'])

        self.validate()

        msg = 'Successfully logged in with username & password'
        self._log.debug(msg)

    @property
    def is_logged_in(self):
        return bool(self.http_client.auth)


class AuthKey(AuthMixins, AuthBase):
    _API_VERSION = 1
    ''':obj:`int`: Version of the API this ApiClient is made for.'''

    _API_PATH = 'api/V{version}/'.format(version=_API_VERSION)
    ''':obj:`str`: Base path of API.'''

    def __init__(self, http_client, key, secret):
        self._log = LOG.getChild(self.__class__.__name__)
        ''':obj:`logging.Logger`: Logger for this object.'''

        self._http_client = http_client
        ''':obj:`axonius_api_client.http.HttpClient`: HTTP Client.'''

        self._creds = {'api-key': key, 'api-secret': secret}
        ''':obj:`dict`: Credential store.'''

        self.login()

    def login(self):
        self.logout()

        self.http_client.session.headers.update(self._creds)

        self.validate()

        msg = 'Successfully logged in with API key & secret'
        self._log.debug(msg)

    @property
    def is_logged_in(self):
        headers = self.http_client.session.headers
        return all([headers.get('api-key', None), headers.get('api-secret', None)])
