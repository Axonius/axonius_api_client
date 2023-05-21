"""Easy all-in-one connection handler."""
import logging
import logging.handlers
import platform
import re
import types
import typing as t

import requests

from . import api, logs, tools, version
from .auth import AuthApiKey, AuthCredentials, AuthModel, AuthNull
from .constants.ctypes import PathLike
from .constants.logs import (
    LOG_FILE_MAX_FILES,
    LOG_FILE_MAX_MB,
    LOG_FILE_NAME,
    LOG_FILE_PATH,
    LOG_FMT_BRIEF,
    LOG_FMT_VERBOSE,
    LOG_LEVEL_API,
    LOG_LEVEL_AUTH,
    LOG_LEVEL_CONSOLE,
    LOG_LEVEL_ENDPOINTS,
    LOG_LEVEL_FILE,
    LOG_LEVEL_PACKAGE,
)
from .exceptions import ConnectError, InvalidCredentials
from .http import Http, T_Cookies, T_Headers
from .projects import cert_human
from .projects.cf_token import constants as cf_constants
from .setup_env import get_env_ax


class Connect:
    """Easy all-in-one connection handler for using the API client.

    Examples:
        >>> #!/usr/bin/env python
        >>> # -*- coding: utf-8 -*-
        >>> '''Base example for setting up the API client.'''
        >>> import axonius_api_client as axonapi
        >>>
        >>> # get the URL, API key, API secret, & certwarn from the default ".env" file
        >>> client_args = axonapi.get_env_connect()
        >>>
        >>> # OR override OS env vars with the values from a custom .env file
        >>> # client_args = axonapi.get_env_connect(ax_env="/path/to/envfile", override=True)
        >>>
        >>> # create a client using the url, key, and secret from OS env
        >>> client = axonapi.Connect(**client_args)
        >>>
        >>> j = client.jdump  # json dump helper
        >>>
        >>> client.start()  # connect to axonius
        >>>
        >>> # client.activity_logs                 # get audit logs
        >>> # client.adapters                      # get adapters and update adapter settings
        >>> # client.adapters.cnx                  # CRUD for adapter connections
        >>> # client.dashboard                     # get/start/stop discovery cycles
        >>> # client.dashboard_spaces              # CRUD for dashboard spaces
        >>> # client.data_scopes                   # CRUD for data scopes
        >>> # client.devices                       # get device assets
        >>> # client.devices.fields                # get field schemas for device assets
        >>> # client.devices.labels                # add/remove/get tags for device assets
        >>> # client.devices.saved_queries         # CRUD for saved queries for device assets
        >>> # client.enforcements                  # CRUD for enforcements
        >>> # client.folders                       # CRUD for folders
        >>> # client.folders.enforcements          # CRUD for enforcements folders
        >>> # client.folders.queries               # CRUD for queries folders
        >>> # client.instances                     # get instances and instance meta data
        >>> # client.openapi                       # get openapi spec
        >>> # client.meta                          # get product meta data
        >>> # client.remote_support                # include_output/disable remote support settings
        >>> # client.settings_global               # get/update global system settings
        >>> # client.settings_gui                  # get/update gui system settings
        >>> # client.settings_ip                   # get/update identity provider system settings
        >>> # client.settings_lifecycle            # get/update lifecycle system settings
        >>> # client.signup                        # initial signup, password resets
        >>> # client.system_roles                  # CRUD for system roles
        >>> # client.system_users                  # CRUD for system users
        >>> # client.users                         # get user assets
        >>> # client.users.fields                  # get field schemas for user assets
        >>> # client.users.labels                  # add/remove/get tags for user assets
        >>> # client.users.saved_queries           # CRUD for saved queries for user assets
        >>> # client.vulnerabilities               # get vulnerability assets
        >>> # client.vulnerabilities.fields        # get field schemas for vulnerability assets
        >>> # client.vulnerabilities.labels        # add/remove/get tags for vulnerability assets
        >>> # client.vulnerabilities.saved_queries # CRUD for saved queries for vulnerability assets
    """

    TOOLS: types.ModuleType = tools
    """Tools module."""

    LOG_LOGGER: logging.Logger = logs.LOG
    """Logger for the entire package, where console and file output handlers will be attached to."""

    LOG: t.Optional[logging.Logger] = None
    """Logger for this class."""

    LOG_HTTP_MAX: bool = False
    """Shortcut to include_output ALL http logging *warning: very heavy log output*."""

    STARTED: bool = False
    """Flag to indicate if client has been started."""

    WRAPERROR: bool = True
    """Flag to indicate if client should wrap exceptions."""

    _url: str = ""
    """Initially supplied URL of the Axonius instance."""

    ARGS_HANDLER_CON: dict = {}
    """Arguments to use when setting up console logging."""

    ARGS_HANDLER_FILE: dict = {}
    """Arguments to use when setting up file logging."""

    ARGS_API: dict = {}
    """Arguments to use when setting up models."""

    ARGS_ORIG: dict = {}
    """Original arguments supplied to the constructor."""

    HANDLER_CON: t.Optional[logging.StreamHandler] = None
    """Console logging handler."""

    HANDLER_FILE: t.Optional[logging.handlers.RotatingFileHandler] = None
    """File logging handler."""

    http: Http = None
    HTTP: Http = None
    """HTTP client."""

    auth: AuthModel = None
    AUTH: AuthModel = None
    """Authentication handler."""

    AUTH_NULL: AuthModel = None
    """Auth model for authenticating with no auth."""

    CREDENTIALS: bool = False
    """Flag to indicate if key & secret are actually username & password."""

    API_CACHE: t.Dict[t.Type[api.ModelMixins], api.ModelMixins] = None
    """Cache for API Models."""

    API_ATTRS: t.List[str] = [
        "activity_logs",
        "adapters",
        "dashboard",
        "dashboard_spaces",
        "data_scopes",
        "devices",
        "enforcements",
        "folders",
        "instances",
        "meta",
        "openapi",
        "remote_support",
        "settings_global",
        "settings_gui",
        "settings_ip",
        "settings_lifecycle",
        "signup",
        "system_roles",
        "system_users",
        "users",
        "vulnerabilities",
    ]
    """Attributes that are API Models."""

    API_LOG_LEVEL: t.Union[int, str] = LOG_LEVEL_API
    """Log level for API Models."""

    REASON_RES: t.List[t.Pattern] = [
        re.compile(r".*?object at.*?>: ([a-zA-Z0-9\]\[: ]+)"),
        re.compile(r".*?] (.*) "),
    ]
    """Patterns to look for in exceptions that we can pretty up for user display."""

    PKG_VERSION: str = version.__version__
    """Version of this package."""

    PY_VERSION: str = platform.python_version()
    """Version of Python that this package is running on."""

    ABOUT_CACHE: t.Optional[dict] = None
    """Cached data from the /about endpoint."""

    HTTP_MAX: str = """log_request_body = True
log_response_body = True
log_level_http = "debug"
log_level_package = "debug"
log_level_console = "debug"
log_level_file = "debug"
log_request_attrs = "all"
log_response_attrs = "all"
log_body_lines = 10000
"""
    """Override values used when log_http_max is True."""

    HTTP_MAX_CLI: str = ", ".join(HTTP_MAX.splitlines())
    """CLI Help string for log_http_max."""

    def __init__(  # noqa: PLR0913
        self,
        url: str,
        key: str,
        secret: str,
        log_console: bool = False,
        log_file: bool = False,
        log_file_rotate: bool = False,
        certpath: t.Optional[PathLike] = None,
        certverify: bool = False,
        certwarn: bool = True,
        proxy: t.Optional[str] = None,
        headers: t.Optional[T_Headers] = None,
        cookies: t.Optional[T_Cookies] = None,
        credentials: bool = False,
        timeout_connect: t.Optional[t.Union[int, float]] = Http.CONNECT_TIMEOUT,
        timeout_response: t.Optional[t.Union[int, float]] = Http.RESPONSE_TIMEOUT,
        cert_client_key: t.Optional[PathLike] = None,
        cert_client_cert: t.Optional[PathLike] = None,
        cert_client_both: t.Optional[PathLike] = None,
        save_history: bool = False,
        log_level: t.Union[str, int] = "debug",
        log_request_attrs: t.Optional[t.Union[str, t.Iterable[str]]] = None,
        log_response_attrs: t.Optional[t.Union[str, t.Iterable[str]]] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        log_logger: logging.Logger = LOG_LOGGER,
        log_level_package: t.Union[str, int] = LOG_LEVEL_PACKAGE,
        log_level_endpoints: t.Union[str, int] = LOG_LEVEL_ENDPOINTS,
        log_level_http: t.Union[str, int] = Http.LOG_LEVEL,
        log_level_auth: t.Union[str, int] = LOG_LEVEL_AUTH,
        log_level_api: t.Union[str, int] = LOG_LEVEL_API,
        log_level_console: t.Union[str, int] = LOG_LEVEL_CONSOLE,
        log_level_file: t.Union[str, int] = LOG_LEVEL_FILE,
        log_console_fmt: str = LOG_FMT_BRIEF,
        log_http_max: bool = LOG_HTTP_MAX,
        log_file_fmt: str = LOG_FMT_VERBOSE,
        log_file_name: t.Optional[PathLike] = LOG_FILE_NAME,
        log_file_path: t.Optional[PathLike] = LOG_FILE_PATH,
        log_file_max_mb: int = LOG_FILE_MAX_MB,
        log_file_max_files: int = LOG_FILE_MAX_FILES,
        log_hide_secrets: bool = True,
        log_body_lines: int = Http.LOG_BODY_LINES,
        wraperror: bool = True,
        cf_token: t.Optional[str] = None,
        cf_url: t.Optional[str] = None,
        cf_path: t.Optional[PathLike] = cf_constants.CF_PATH,
        cf_run: bool = cf_constants.CLIENT_RUN,
        cf_run_login: bool = cf_constants.FLOW_RUN_LOGIN,
        cf_run_access: bool = cf_constants.FLOW_RUN_ACCESS,
        cf_env: bool = cf_constants.FLOW_ENV,
        cf_echo: bool = cf_constants.FLOW_ECHO,
        cf_echo_verbose: bool = cf_constants.FLOW_ECHO_VERBOSE,
        cf_error: bool = cf_constants.CLIENT_ERROR,
        cf_error_login: bool = cf_constants.FLOW_ERROR,
        cf_error_access: bool = cf_constants.FLOW_ERROR,
        cf_timeout_access: t.Optional[int] = cf_constants.TIMEOUT_ACCESS,
        cf_timeout_login: t.Optional[int] = cf_constants.TIMEOUT_LOGIN,
        http: t.Optional[Http] = None,
        auth: t.Optional[AuthModel] = None,
        auth_null: t.Optional[AuthModel] = None,
        **kwargs: t.Dict[str, t.Any],
    ) -> None:
        """Easy all-in-one connection handler.

        Args:
            url: URL, hostname, or IP address of Axonius instance
            key: API Key from account page in Axonius instance
            secret: API Secret from account page in Axonius instance
            log_console: include_output logging to console
            log_file: include_output logging to file
            certpath: path to CA bundle file to use when verifying certs offered by url
            certverify: raise exception if cert is self-signed or only if cert is invalid
            certwarn: show insecure warning once or never show insecure warning
            proxy: proxy to use when making https requests to url
            headers: additional headers to supply with every request
            cookies: additional cookies to supply with every request
            credentials: treat key as username as secret as password
            timeout_connect: seconds to wait for connections to open to url
            timeout_response: seconds to wait for responses from url
            cert_client_key: file with private key to offer to url
            cert_client_cert: file with client cert to offer to url
            cert_client_both: file with client cert and private key to offer to url
            save_history: save history of responses to Http.HISTORY
            log_level: log level to use for this object
            log_request_attrs: list of request attributes to log
            log_response_attrs: list of response attributes to log
            log_request_body: log request body
            log_response_body: log response body
            log_logger: Logger for the entire package, where console and file output
                handlers will be attached to
            log_level_package: log level to use for package root logger
            log_level_endpoints: log level to use for endpoint loggers
            log_level_http: log level to use for http loggers
            log_level_auth: log level to use for auth loggers
            log_level_api: log level to use for api loggers
            log_level_console: log level to use for console loggers
            log_level_file: log level to use for file loggers
            log_console_fmt: format string to use for console logging
            log_file_fmt: format string to use for file logging
            log_file_name: name of file to log to
            log_file_path: path to directory to log to
            log_file_max_mb: max size of log file in MB
            log_file_max_files: max number of log files to keep
            log_file_rotate: rotate log file on startup
            log_body_lines: max length of request/response body to log
            log_hide_secrets: hide secrets in logs
            log_http_max: Shortcut to include_output ALL http logging *warning: heavy log output*
            wraperror: wrap certain errors in a more user friendly format
            cf_url: URL to use in `access token` and `access login` commands,
                will fallback to url if not supplied
            cf_token: access token supplied by user, will be checked for validity if not empty
            cf_env: if no token supplied, try to get token from OS env var CF_TOKEN
            cf_run: if no token supplied or in OS env vars, try to get token from `access token` and
                `access login` commands
            cf_run_access: if run is True, try to get token from `access token`,
            cf_run_login: if run is True and no token returned from `access token` command,
                try to get token from `access login` command
            cf_path: path to cloudflared binary to run, can be full path or path in OS env var $PATH
            cf_timeout_access: timeout for `access token` command in seconds
            cf_timeout_login: timeout for `access login` command in seconds
            cf_error: raise error if an invalid token is found or no token can be found
            cf_error_access: raise exc if `access token` command fails and login is False
            cf_error_login: raise exc if `access login` command fails
            cf_echo: echo commands and results to stderr
            cf_echo_verbose: echo more to stderr
            http: http object to use for this connection
            auth: auth model to use for this connection
            auth_null: null auth model to use for this connection
            **kwargs: unused
        """
        self._url: str = url
        self.__key: str = key
        self.__secret: str = secret
        self.CLIENT = self
        self.API_CACHE: dict = {}
        self.ARGS_ORIG: dict = kwargs
        self.LOG_LOGGER: logging.Logger = log_logger
        self.LOG: logging.Logger = logs.get_obj_log(obj=self, log_level=log_level)
        self.LOG_HTTP_MAX: bool = tools.coerce_bool(log_http_max)
        self.CREDENTIALS: bool = tools.coerce_bool(credentials)

        if self.LOG_HTTP_MAX:
            log_request_body = True
            log_response_body = True
            log_level_http = "debug"
            log_level_package = "debug"
            log_level_console = "debug"
            log_level_file = "debug"
            log_request_attrs = "all"
            log_response_attrs = "all"
            if not isinstance(log_body_lines, int) or (
                isinstance(log_body_lines, int)
                and log_body_lines < 10000  # noqa: PLR2004
            ):
                log_body_lines = 10000

        self.ARGS_HANDLER_CON: dict = {
            "obj": log_logger,
            "level": log_level_console,
            "fmt": log_console_fmt,
        }
        self.ARGS_HANDLER_FILE: dict = {
            "obj": log_logger,
            "level": log_level_file,
            "file_path": log_file_path,
            "file_name": log_file_name,
            "max_mb": log_file_max_mb,
            "max_files": log_file_max_files,
            "fmt": log_file_fmt,
        }
        self.ARGS_HTTP: dict = {
            "url": url,
            "https_proxy": proxy,
            "certpath": certpath,
            "certwarn": certwarn,
            "certverify": certverify,
            "cert_client_both": cert_client_both,
            "cert_client_cert": cert_client_cert,
            "cert_client_key": cert_client_key,
            "log_level": log_level_http,
            "log_body_lines": log_body_lines,
            "log_request_attrs": log_request_attrs,
            "log_response_attrs": log_response_attrs,
            "log_request_body": log_request_body,
            "log_response_body": log_response_body,
            "save_history": save_history,
            "connect_timeout": timeout_connect,
            "response_timeout": timeout_response,
            "headers": headers,
            "cookies": cookies,
            "cf_url": cf_url,
            "cf_token": cf_token,
            "cf_env": cf_env,
            "cf_run": cf_run,
            "cf_run_login": cf_run_login,
            "cf_run_access": cf_run_access,
            "cf_path": cf_path,
            "cf_timeout_access": cf_timeout_access,
            "cf_timeout_login": cf_timeout_login,
            "cf_error": cf_error,
            "cf_error_access": cf_error_access,
            "cf_error_login": cf_error_login,
            "cf_echo": cf_echo,
            "cf_echo_verbose": cf_echo_verbose,
        }

        self.set_wraperror(wraperror)
        self.set_log_hide_secrets(value=log_hide_secrets)
        self.set_log_level_api(value=log_level_api)
        self.set_log_level_package(value=log_level_package)
        self.set_log_level_endpoints(value=log_level_endpoints)
        self.control_log_file(enable=log_file, rotate=log_file_rotate)
        self.control_log_console(enable=log_console)
        self.HTTP = self.http = self._init_http(http=http)
        self.AUTH = self.auth = self._init_auth(auth=auth, log_level=log_level_auth)
        self.AUTH_NULL: AuthModel = self._init_auth_null(
            auth_null=auth_null,
            log_level=log_level_auth,
        )
        self._init()

    def start(self) -> None:
        """Connect to and authenticate with Axonius."""
        if not self.STARTED:
            sysinfo_dump: dict = tools.sysinfo()
            self.LOG.debug(f"SYSTEM INFO: {tools.json_dump(sysinfo_dump)}")

            try:
                self.AUTH.login()
            except Exception as exc:  # noqa: BLE001
                if not self.WRAPERROR:
                    raise

                pre = f"Unable to connect to {self.url!r}"
                connect_exc = ConnectError(f"{pre}: {exc}")

                if isinstance(exc, requests.ConnectTimeout):
                    timeout = self.HTTP.CONNECT_TIMEOUT
                    msg = f"{pre}: connection timed out after {timeout} seconds"
                    connect_exc = ConnectError(msg)
                elif isinstance(exc, requests.ConnectionError):
                    reason = self._get_exc_reason(exc=exc)
                    connect_exc = ConnectError(f"{pre}: {reason}")
                elif isinstance(exc, InvalidCredentials):
                    connect_exc = ConnectError(f"{pre}: Invalid Credentials supplied")

                connect_exc.exc = exc
                raise connect_exc from exc

            self.STARTED = True
            self.LOG.info(str(self))

    # --> MODELS
    @property
    def activity_logs(self) -> api.ActivityLogs:
        """Work with activity logs."""
        return self._get_model(model=api.ActivityLogs)

    @property
    def adapters(self) -> api.Adapters:
        """Work with adapters and adapter connections."""
        return self._get_model(model=api.Adapters)

    @property
    def dashboard(self) -> api.Dashboard:
        """Work with discovery cycles."""
        return self._get_model(model=api.Dashboard)

    @property
    def dashboard_spaces(self) -> api.DashboardSpaces:
        """Work with dashboard spaces."""
        return self._get_model(model=api.DashboardSpaces)

    @property
    def data_scopes(self) -> api.DataScopes:
        """Work with data scopes."""
        return self._get_model(model=api.DataScopes)

    @property
    def devices(self) -> api.Devices:
        """Work with device assets."""
        return self._get_model(model=api.Devices)

    @property
    def enforcements(self) -> api.Enforcements:
        """Work with Enforcement Center."""
        return self._get_model(model=api.Enforcements)

    @property
    def folders(self) -> api.Folders:
        """Work with folders for enforcements and queries."""
        return self._get_model(model=api.Folders)

    @property
    def instances(self) -> api.Instances:
        """Work with instances."""
        return self._get_model(model=api.Instances)

    @property
    def openapi(self) -> api.OpenAPISpec:
        """Work with the OpenAPI specification file."""
        return self._get_model(model=api.OpenAPISpec)

    @property
    def meta(self) -> api.Meta:
        """Work with instance metadata."""
        return self._get_model(model=api.Meta)

    @property
    def remote_support(self) -> api.RemoteSupport:
        """Work with configuring remote support."""
        return self._get_model(model=api.RemoteSupport)

    @property
    def settings_global(self) -> api.SettingsGlobal:
        """Work with core system settings."""
        return self._get_model(model=api.SettingsGlobal)

    @property
    def settings_gui(self) -> api.SettingsGui:
        """Work with gui system settings."""
        return self._get_model(model=api.SettingsGui)

    @property
    def settings_ip(self) -> api.SettingsIdentityProviders:
        """Work with identity providers settings."""
        return self._get_model(model=api.SettingsIdentityProviders)

    @property
    def settings_lifecycle(self) -> api.SettingsLifecycle:
        """Work with lifecycle system settings."""
        return self._get_model(model=api.SettingsLifecycle)

    @property
    def signup(self) -> api.Signup:
        """Perform initial signup, password reset, and other unauthenticated endpoints."""
        return self._get_model(model=api.Signup, start=False, auth=self.AUTH_NULL)

    @property
    def system_users(self) -> api.SystemUsers:
        """Work with system users."""
        return self._get_model(model=api.SystemUsers)

    @property
    def system_roles(self) -> api.SystemRoles:
        """Work with system roles."""
        return self._get_model(model=api.SystemRoles)

    @property
    def users(self) -> api.Users:
        """Work with user assets."""
        return self._get_model(model=api.Users)

    @property
    def vulnerabilities(self) -> api.Vulnerabilities:
        """Work with vulnerability assets."""
        return self._get_model(model=api.Vulnerabilities)

    def set_wraperror(self, value: bool = True) -> None:
        """Set whether to wrap errors in a more user-friendly format."""
        self.WRAPERROR = tools.coerce_bool(value)

    # <-- METHODS

    @staticmethod
    def set_log_hide_secrets(value: bool = True) -> None:
        """Set whether to hide secrets in logs."""
        logs.HideFormatter.HIDE_ENABLED = tools.coerce_bool(value)

    def set_log_level_console(
        self,
        value: t.Union[str, int] = LOG_LEVEL_CONSOLE,
    ) -> None:
        """Set the log level for this client's console output."""
        if isinstance(self.ARGS_HANDLER_CON, dict):
            self.ARGS_HANDLER_CON["level"] = logs.str_level(value)
        if self.HANDLER_CON:
            logs.set_log_level(obj=self.HANDLER_CON, level=value)

    def set_log_level_file(self, value: t.Union[str, int] = LOG_LEVEL_FILE) -> None:
        """Set the log level for this client's file output."""
        if isinstance(self.ARGS_HANDLER_FILE, dict):
            self.ARGS_HANDLER_FILE["level"] = logs.str_level(value)
        if self.HANDLER_FILE:
            logs.set_log_level(obj=self.HANDLER_FILE, level=value)

    def set_log_level_api(self, value: t.Union[str, int] = LOG_LEVEL_API) -> None:
        """Set the log level for this client's api objects."""
        self.API_LOG_LEVEL: str = logs.str_level(value)
        for obj in self.API_CACHE.values():
            if isinstance(obj, api.ModelMixins):
                logs.set_log_level(obj=obj.LOG, level=self.API_LOG_LEVEL)

    def set_log_level_connect(self, value: t.Union[str, int] = "debug") -> None:
        """Set the log level for this client."""
        if self.LOG:
            logs.set_log_level(obj=self.LOG, level=value)

    def set_log_level_http(self, value: t.Union[str, int] = Http.LOG_LEVEL) -> None:
        """Set the log level for this client's http object."""
        if isinstance(self.HTTP, Http):
            logs.set_log_level(obj=self.HTTP.LOG, level=value)

    def set_log_level_auth(self, value: t.Union[str, int] = LOG_LEVEL_AUTH) -> None:
        """Set the log level for this client's auth objects."""
        for obj in self.AUTH, self.AUTH_NULL:
            if isinstance(obj, AuthModel):
                logs.set_log_level(obj=obj.LOG, level=value)

    def set_log_level_package(
        self,
        value: t.Union[str, int] = LOG_LEVEL_PACKAGE,
    ) -> None:
        """Set the log level for this client's package."""
        logs.set_log_level(obj=self.LOG_LOGGER, level=value)

    @staticmethod
    def set_log_level_endpoints(value: t.Union[str, int] = LOG_LEVEL_ENDPOINTS) -> None:
        """Set the log level for this client's endpoints."""
        from axonius_api_client.api.api_endpoint import (
            LOGGER as LOGGER_ENDPOINT,
        )

        logs.set_log_level(obj=LOGGER_ENDPOINT, level=value)

    def control_log_console(self, enable: bool = False) -> bool:
        """Add logging to console for this client."""
        enable = tools.coerce_bool(enable)
        if enable and not self.HANDLER_CON:
            self.HANDLER_CON = logs.add_stderr(**self.ARGS_HANDLER_CON)
            self.LOG.debug("Logging to console enabled.")
            return True
        if not enable and self.HANDLER_CON:
            self.LOG.debug("Logging to console disabled.")
            self.HANDLER_CON.close()
            logs.del_stderr(obj=self.LOG_LOGGER)
            self.HANDLER_CON = None
            return True
        return False

    def control_log_file(self, enable: bool = False, rotate: bool = False) -> bool:
        """Add logging to file for this client."""
        enable = tools.coerce_bool(enable)
        if enable and not self.HANDLER_FILE:
            self.HANDLER_FILE = logs.add_file(**self.ARGS_HANDLER_FILE)
            self.LOG.debug("Logging to file enabled.")
            return True
        self.rotate_log_files(value=rotate)
        if not enable and self.HANDLER_FILE:
            self.LOG.debug("Logging to file disabled.")
            self.HANDLER_FILE.close()
            logs.del_file(obj=self.LOG_LOGGER)
            self.HANDLER_FILE = None
            return True
        return False

    def rotate_log_files(self, value: bool = False) -> None:
        """Rollover log file."""
        value = tools.coerce_bool(value)
        if value and self.HANDLER_FILE:
            self.LOG.debug("Forcing file logs to rotate")
            self.HANDLER_FILE.flush()
            try:
                self.HANDLER_FILE.doRollover()
            except Exception as exc:  # pragma: no cover  # noqa: BLE001
                self.LOG.exception("Failed to force file logs to rotate: %s", exc)
            else:
                self.LOG.debug("Forced file logs to rotate")

    @property
    def url(self) -> str:
        """Get the URL of the current instance."""
        return self.HTTP.url if self.HTTP else self._url

    @property
    def api_keys(self) -> dict:
        """Get the API keys for the current user."""
        return self.AUTH.get_api_keys()

    @property
    def current_user(self) -> t.Optional[api.json_api.account.CurrentUser]:
        """Get the current user (returns 404 for service accounts)."""
        try:
            return self.AUTH.get_current_user()
        except Exception:  # noqa: BLE001
            return None

    @property
    def about(self) -> dict:
        """Cached data from the /about endpoint."""
        if self.ABOUT_CACHE:
            return self.ABOUT_CACHE
        value = self.meta.about(error=False)
        if value:
            self.ABOUT_CACHE = value
        return value

    @property
    def version(self) -> str:
        """Get the Axonius instance version."""
        data = "none yet"
        if self.STARTED:
            data = (
                self.about.get("Version")
                or self.about.get("Installed Version")
                or "DEMO"
            )
            data = data.replace("_", ".")
        return data

    @property
    def build_date(self) -> str:
        """Get the Axonius instance build date."""
        data = "none yet"
        if self.STARTED:
            data = self.about.get("Build Date", "UNKNOWN")
        return data

    @property
    def str_ax_version(self) -> str:
        """Get the Axonius instance version & build date for use in str."""
        days = f"({tools.dt_days_ago(self.build_date)} days ago)"
        return (
            f"Axonius Version {self.version!r}, Build Date: {self.build_date!r} {days}"
        )

    @property
    def str_ax_user(self) -> str:
        """Get the Axonius instance user for use in str."""
        value = "User: ??"
        if self.STARTED and self.current_user:
            value = self.current_user.str_connect
        return value

    @property
    def ssl_days_left(self) -> t.Optional[int]:
        """Get the number of days left until the SSL certificate expires."""
        value = None
        if isinstance(self.HTTP, Http):
            cert: t.Optional[cert_human.Cert] = self.HTTP.get_cert()
            if isinstance(cert, cert_human.Cert):
                value = tools.dt_days_ago(cert.not_valid_after, from_now=False)
        return value

    @property
    def str_ax_cert(self) -> str:
        """Get the Axonius instance SSL certificate for use in str."""
        value = "SSL: ??"
        if isinstance(self.HTTP, Http):
            cert: t.Optional[cert_human.Cert] = self.HTTP.get_cert()
            if isinstance(cert, cert_human.Cert):
                not_valid_after = str(cert.not_valid_after)
                value = f"SSL Issued To: {cert.subject_short!r}, Expires On: {not_valid_after!r}"
        return value

    @property
    def str_state(self) -> str:
        """Get the connection state for use in str."""
        value = "Not connected"
        if self.STARTED:
            value = "Connected"
        value = f"{value} to {self.url!r}, CLIENT v{self.PKG_VERSION}, PYTHON v{self.PY_VERSION}"
        banner = get_env_ax().get("AX_BANNER")
        if banner:
            value = f"{value} [{banner}]"
        return value

    @staticmethod
    def jdump(obj: t.Any, **kwargs) -> None:
        """Print object as JSON."""
        tools.jdump(obj=obj, **kwargs)

    def __str__(self) -> str:
        """Show object info."""
        items: t.List[str] = [
            self.str_state,
            self.str_ax_version,
            self.str_ax_cert,
            self.str_ax_user,
        ]
        return "\n".join(x for x in items if x)

    def __repr__(self) -> str:
        """Show object info."""
        return self.__str__()

    @classmethod
    def _get_exc_reason(cls, exc: Exception) -> str:
        """Trim exceptions down to a more user-friendly display.

        Uses :attr:`REASON_RES` to do regex substitutions.
        """
        reason = str(exc)
        for reason_re in cls.REASON_RES:
            if reason_re.search(reason):
                return reason_re.sub(r"\1", reason).rstrip("')")
        return reason

    def _check_binding(self, value: t.Any) -> t.Any:
        """Check if an object is already bound to a different client."""
        client = getattr(value, "CLIENT", value)
        if isinstance(client, self.__class__) and client is not self:
            err = f"{value} is already set to {client!r} and cannot be set to {self!r}"
            raise ConnectError(err)
        value.CLIENT = self
        return value

    def _init_http(self, http: t.Optional[Http] = None) -> Http:
        """Initialize the HTTP object."""
        if not isinstance(http, Http):
            http: Http = Http(**self.ARGS_HTTP)
        return self._check_binding(http)

    def _init_auth(
        self,
        auth: t.Optional[AuthModel] = None,
        log_level: t.Union[str, int] = LOG_LEVEL_AUTH,
    ) -> AuthModel:
        """Initialize the Auth object."""
        if not isinstance(auth, AuthModel):
            if self.CREDENTIALS:
                auth: AuthCredentials = AuthCredentials(
                    username=self.__key,
                    password=self.__secret,
                    http=self.http,
                    log_level=log_level,
                )
            else:
                auth: AuthApiKey = AuthApiKey(
                    key=self.__key,
                    secret=self.__secret,
                    http=self.http,
                    log_level=log_level,
                )
        return self._check_binding(auth)

    def _init_auth_null(
        self,
        auth_null: t.Optional[AuthModel] = None,
        log_level: t.Union[str, int] = LOG_LEVEL_AUTH,
    ) -> AuthModel:
        """Initialize the null Auth object."""
        if not isinstance(auth_null, AuthModel):
            auth_null: AuthNull = AuthNull(http=self.http, log_level=log_level)
        return self._check_binding(auth_null)

    def _init(self):
        """Custom init for this class."""

    def _get_model(
        self,
        model: t.Type[api.ModelMixins],
        start: bool = True,
        auth: t.Optional[AuthModel] = None,
    ) -> t.Any:
        """Create or get an API model.

        Args:
            model: model to create or get
            start: start :attr:`AUTH` if not already started
            auth: auth to use for this model, if not supplied default to :attr:`AUTH`

        Returns:
            model instance
        """
        if start:
            self.start()

        if model in self.API_CACHE:
            return self.API_CACHE[model]

        if not isinstance(auth, AuthModel):
            auth = self.AUTH

        self.API_CACHE[model] = model(auth=auth, log_level=self.API_LOG_LEVEL)
        return self.API_CACHE[model]
