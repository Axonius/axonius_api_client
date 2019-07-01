# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

from . import exceptions
from . import http


@six.add_metaclass(abc.ABCMeta)
class AuthBase(object):
    @abc.abstractmethod
    def login(self):
        raise NotImplementedError

    @abc.abstractmethod
    def logout(self):
        raise NotImplementedError

    @abc.abstractproperty
    def is_logged_in(self):
        raise NotImplementedError


class AuthClientUser(http.HttpClient, AuthBase):
    _API_VERSION = 1
    ''':obj:`int`: Version of the API this ApiClient is made for.'''

    _API_PATH = 'api/V{version}/'.format(version=_API_VERSION)
    ''':obj:`str`: Base path of API.'''

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        bits = ['url={!r}'.format(self._url), 'is_logged_in={!r}'.format(self.is_logged_in)]
        bits = '({})'.format(', '.join(bits))
        cls = '{c.__module__}.{c.__name__}'.format(c=self.__class__)
        return '{cls}{bits}'.format(cls=cls, bits=bits)

    # pylint: disable=W0221
    def login(self, username, password):
        self.logout()

        self._session.auth = (username, password)

        response = self(method='get', path=self._API_PATH, route='devices/count')

        if response.status_code in [401, 403]:
            msg = 'Login failed!'
            raise exceptions.InvalidCredentials(msg)

        response.raise_for_status()

        msg = 'Successfully logged in username {username!r}'
        msg = msg.format(username=username)
        self._log.info(msg)

    def logout(self):
        self._session.cookies.clear()
        self._session.headers.pop('api-key', None)
        self._session.headers.pop('api-secret', None)
        self._session.auth = None

    @property
    def is_logged_in(self):
        return bool(self._session.auth)


class AuthClientKey(http.HttpClient, AuthBase):
    _API_VERSION = 1
    ''':obj:`int`: Version of the API this ApiClient is made for.'''

    _API_PATH = 'api/V{version}/'.format(version=_API_VERSION)
    ''':obj:`str`: Base path of API.'''

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        bits = ['url={!r}'.format(self._url), 'is_logged_in={!r}'.format(self.is_logged_in)]
        bits = '({})'.format(', '.join(bits))
        cls = '{c.__module__}.{c.__name__}'.format(c=self.__class__)
        return '{cls}{bits}'.format(cls=cls, bits=bits)

    # pylint: disable=W0221
    def login(self, key, secret):
        self.logout()
        creds = {'api-key': key, 'api-secret': secret}
        self._session.headers.update(creds)

        response = self(method='get', path=self._API_PATH, route='devices/count')

        if response.status_code in [401, 403]:
            msg = 'Login failed!'
            raise exceptions.InvalidCredentials(msg)

        response.raise_for_status()

        msg = 'Successfully logged in with API key & secret'
        self._log.info(msg)

    def logout(self):
        self._session.cookies.clear()
        self._session.headers.pop('api-key', None)
        self._session.headers.pop('api-secret', None)
        self._session.auth = None

    @property
    def is_logged_in(self):
        headers = self._session.headers
        return all([headers.get('api-key', None), headers.get('api-secret', None)])
