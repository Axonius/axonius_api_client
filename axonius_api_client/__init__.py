# -*- coding: utf-8 -*-
"""Python API Client for Axonius.

Examples:
    >>> import os
    >>>
    >>> import axonius_api_client as axonapi  # noqa: F401
    >>> from axonius_api_client.connect import Connect
    >>> from axonius_api_client.constants import load_dotenv
    >>>
    >>> # read the API key, API secret, and URL from a ".env" file
    >>> load_dotenv()
    >>> AX_URL = os.environ["AX_URL"]
    >>> AX_KEY = os.environ["AX_KEY"]
    >>> AX_SECRET = os.environ["AX_SECRET"]
    >>>
    >>> # create a client using the url, key, and secret
    >>> ctx = Connect(url=AX_URL, key=AX_KEY, secret=AX_SECRET)
    >>>
    >>> # start the client, will perform login to URL using key & secret
    >>> ctx.start()
    >>>
    >>> # work with device assets
    >>> devices = ctx.devices
    >>>
    >>> # work with user assets
    >>> users = ctx.users
    >>>
    >>> # work with adapters and adapter connections
    >>> adapters = ctx.adapters
    >>>
    >>> # work with enforcements
    >>> enforcements = ctx.enforcements
    >>>
    >>> # work with users, roles, global settings, and more
    >>> system = ctx.system
    >>>
    >>> # work with instances
    >>> instances = ctx.instances
    >>>
    >>> # work with dashboards and discovery cycles
    >>> dashboard = ctx.dashboard

"""
from . import (api, auth, cli, constants, data, exceptions, http, logs, tools,
               url_parser, version, wizard)
from .api import (Adapters, Devices, Enforcements, Instances, Signup, System,
                  Users)
from .auth import ApiKey
from .connect import Connect
from .http import Http
from .url_parser import UrlParser
from .wizard import Wizard, WizardCsv, WizardText

__version__ = version.__version__
LOG = logs.LOG

__all__ = (
    # Connection handler
    "Connect",
    # http client
    "Http",
    # authentication
    "ApiKey",
    # api
    "Users",
    "Devices",
    "Adapters",
    "Enforcements",
    "System",
    "Signup",
    # wizards
    "Wizard",
    "WizardText",
    "WizardCsv",
    "Instances",
    "UrlParser",
    # modules
    "api",
    "auth",
    "http",
    "exceptions",
    "version",
    "tools",
    "constants",
    "cli",
    "logs",
    "data",
    "wizard",
    "url_parser",
)
