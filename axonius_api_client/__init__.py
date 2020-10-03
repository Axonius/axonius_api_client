# -*- coding: utf-8 -*-
"""Python API Client for Axonius.

See Also:
    :obj:`connect.Connect` for creating a client for using this package.

"""
import logging

from . import setup_env, version

PACKAGE_ROOT: str = __package__
PACKAGE_FILE: str = __file__
VERSION: str = version.__version__
__version__ = VERSION

LOG: logging.Logger = logging.getLogger(PACKAGE_ROOT)
"""root logger used by entire package, named after package."""

DEFAULT_PATH: str = setup_env.DEFAULT_PATH
"""default path to use throughout the package."""

load_dotenv = setup_env.load_dotenv
get_connect_env = setup_env.get_connect_env

load_dotenv()

try:
    from . import (
        api,
        auth,
        cli,
        constants,
        data,
        exceptions,
        http,
        logs,
        tools,
        url_parser,
    )
    from .api import (
        Adapters,
        CentralCore,
        Cnx,
        Dashboard,
        Devices,
        Enforcements,
        Instances,
        Meta,
        RunAction,
        SettingsCore,
        SettingsGui,
        SettingsLifecycle,
        Signup,
        System,
        SystemRoles,
        SystemUsers,
        Users,
        Wizard,
        WizardCsv,
        WizardText,
        routers,
    )
    from .auth import ApiKey
    from .connect import Connect
    from .http import Http
    from .url_parser import UrlParser
except Exception:
    raise


LOG = logs.LOG

__all__ = (
    # API client
    "Connect",
    # HTTP client
    "Http",
    # API authentication
    "ApiKey",
    # API
    "Adapters",
    "CentralCore",
    "Cnx",
    "Dashboard",
    "Devices",
    "Enforcements",
    "Instances",
    "Meta",
    "routers",
    "RunAction",
    "SettingsCore",
    "SettingsGui",
    "SettingsLifecycle",
    "Signup",
    "System",
    "SystemRoles",
    "SystemUsers",
    "UrlParser",
    "Users",
    "Wizard",
    "Wizard",
    "WizardCsv",
    "WizardCsv",
    "WizardText",
    "WizardText",
    # modules
    "api",
    "auth",
    "cli",
    "constants",
    "data",
    "exceptions",
    "http",
    "logs",
    "tools",
    "url_parser",
    "version",
    "DEFAULT_PATH",
)
