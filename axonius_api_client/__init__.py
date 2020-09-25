# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
from . import api, auth, cli, constants, data, exceptions, http, logs, tools, version, wizard
from .api import Adapters, Devices, Enforcements, Instances, Signup, System, Users
from .auth import ApiKey
from .connect import Connect
from .http import Http
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
)
