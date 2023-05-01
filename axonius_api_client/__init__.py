# -*- coding: utf-8 -*-
"""Python API Client for Axonius.

See Also:
    :obj:`connect.Connect` for creating a client for using this package.

"""
import logging
import sys
import pathlib

from . import setup_env, version

PACKAGE_ROOT: str = __package__
PACKAGE_FILE: str = __file__
PACKAGE_PATH: pathlib.Path = pathlib.Path(PACKAGE_FILE).parent.absolute()
PROJECTS_PATH: pathlib.Path = PACKAGE_PATH / "projects"

VERSION: str = version.__version__
__version__ = VERSION

LOG: logging.Logger = logging.getLogger(PACKAGE_ROOT)
"""root logger used by entire package, named after package."""

DEFAULT_PATH: str = setup_env.DEFAULT_PATH
"""default path to use throughout the package."""

load_dotenv = setup_env.load_dotenv
get_env_connect = setup_env.get_env_connect

PRE_DOTENV: dict = setup_env.get_env_ax()
"""AX.* env variables before loading dotenv."""

INIT_DOTENV: str = load_dotenv()
"""Initial path to .env file that was loaded"""

POST_DOTENV: dict = setup_env.get_env_ax()
"""AX.* env variables after loading dotenv."""

# short term hack for projects until they are moved to their own repos
try:
    sys.path.insert(0, str(PROJECTS_PATH))
    from .projects import cf_token, cert_human, url_parser

except Exception:  # pragma: no cover
    raise


try:
    # noinspection PyCompatibility
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
        projects,
    )

    from .api import (
        ActivityLogs,
        Adapters,
        ApiEndpoints,
        Cnx,
        Dashboard,
        DashboardSpaces,
        Devices,
        Enforcements,
        Instances,
        Meta,
        RemoteSupport,
        Runner,
        SettingsGlobal,
        SettingsGui,
        SettingsLifecycle,
        Signup,
        SystemRoles,
        SystemUsers,
        Users,
        Vulnerabilities,
        Wizard,
        WizardCsv,
        WizardText,
        json_api,
    )
    from .auth import AuthApiKey, AuthCredentials, AuthModel, AuthNull
    from .connect import Connect
    from .features import Features
    from .http import Http
except Exception:  # pragma: no cover
    raise


LOG = logs.LOG

__all__ = (
    "PACKAGE_ROOT",
    # API client
    "Connect",
    # HTTP client
    "Http",
    # API authentication
    "AuthApiKey",
    "AuthModel",
    "AuthCredentials",
    "AuthNull",
    # API
    "Adapters",
    "Cnx",
    "Dashboard",
    "DashboardSpaces",
    "Devices",
    "Enforcements",
    "Instances",
    "Meta",
    "RemoteSupport",
    "SettingsGlobal",
    "SettingsGui",
    "SettingsLifecycle",
    "Signup",
    "SystemRoles",
    "SystemUsers",
    "Runner",
    "Users",
    "Wizard",
    "Wizard",
    "WizardCsv",
    "WizardCsv",
    "WizardText",
    "WizardText",
    "ActivityLogs",
    "ApiEndpoints",
    "Features",
    "Vulnerabilities",
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
    "version",
    "json_api",
    # projects
    "projects",
    "cert_human",
    "cf_token",
    "url_parser",
)
