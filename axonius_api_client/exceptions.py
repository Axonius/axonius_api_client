# -*- coding: utf-8 -*-
"""Parent exception and warnings for this package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class PackageError(Exception):
    """Parent exception for all package errors."""


class PackageWarning(Warning):
    """Parent warning all package warnings."""


class InvalidCredentials(PackageError):
    """Error on failed login."""


class MustLogin(PackageError):
    """Error when not logged in."""

    def __init__(self, auth_client):
        self.auth_client = auth_client
        msg = '{auth_client} is not logged in, use login()'
        msg = msg.format(auth_client=auth_client)
        super(MustLogin, self).__init__(msg)
