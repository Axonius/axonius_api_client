# -*- coding: utf-8 -*-
"""Axonius API Client Authentication errors."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .. import exceptions


class AuthError(exceptions.PackageError):
    """Parent exception for all Authentication errors."""


class InvalidCredentials(AuthError):
    """Error on failed login."""

    def __init__(self, auth, exc=None):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.auth.models.AuthBase`):
                Authentication method.
            exc (:obj:`Exception`, optional):
                Original Exception, if any.

                Defaults to: None.

        """
        self.auth = auth
        """:obj:`axonius_api_client.auth.models.AuthBase`: Authentication method."""

        self.exc = exc
        """:obj:`Exception`: Original Exception, if any."""

        msg = "Invalid credentials on {auth} -- exception: {exc}"
        msg = msg.format(auth=auth, exc=exc)
        super(InvalidCredentials, self).__init__(msg)


class NotLoggedIn(AuthError):
    """Error when not logged in."""

    def __init__(self, auth):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.auth.models.AuthBase`):
                Authentication method.

        """
        self.auth = auth
        """:obj:`axonius_api_client.auth.models.AuthBase`: Authentication method."""

        msg = "Must call login() on {auth}"
        msg = msg.format(auth=auth)
        super(NotLoggedIn, self).__init__(msg)


class AlreadyLoggedIn(AuthError):
    """Error when already logged in."""

    def __init__(self, auth):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.auth.models.AuthBase`):
                Authentication method.

        """
        self.auth = auth
        """:obj:`axonius_api_client.auth.models.AuthBase`: Authentication method."""

        msg = "Already logged in on {auth}"
        msg = msg.format(auth=auth)
        super(AlreadyLoggedIn, self).__init__(msg)
