# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from .api import (
    Users,
    Devices,
    Actions,
    Adapters,
    Enforcements,
    routers,
    find_adapter,
    find_field,
    validate_fields,
)
from .auth import AuthUser, AuthKey
from .http import HttpClient, UrlParser
from .exceptions import (
    AxonError,
    ApiError,
    ToolsError,
    AuthError,
    ResponseError,
    InvalidJson,
    ObjectNotFound,
    TooFewObjectsFound,
    TooManyObjectsFound,
    UnknownAdapterName,
    UnknownFieldName,
    InvalidCredentials,
    NotLoggedIn,
    AlreadyLoggedIn,
    HttpError,
    ConnectError,
)
from . import version, tools, constants, cli
from .models import ApiModel, AuthModel
from .connect import Connect

__version__ = version.__version__

LOG = logging.getLogger(__name__)
tools.add_null(obj=LOG)

__all__ = (
    # http
    "HttpClient",
    "UrlParser",
    # misc
    "version",
    "tools",
    "constants",
    "cli",
    # auth
    "AuthUser",
    "AuthKey",
    # models
    "ApiModel",
    "AuthModel",
    # exceptions
    "AxonError",
    "HttpError",
    "ApiError",
    "ToolsError",
    "AuthError",
    "ResponseError",
    "InvalidJson",
    "ObjectNotFound",
    "TooFewObjectsFound",
    "TooManyObjectsFound",
    "UnknownAdapterName",
    "UnknownFieldName",
    "InvalidCredentials",
    "NotLoggedIn",
    "AlreadyLoggedIn",
    "ConnectError",
    # api
    "Users",
    "Devices",
    "Actions",
    "Adapters",
    "Enforcements",
    "routers",
    "find_adapter",
    "find_field",
    "validate_fields",
    # Connection
    "Connect",
)
