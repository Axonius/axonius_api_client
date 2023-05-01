# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import os
import sys
import typing as t

import click

from ..projects.cf_token import constants as cf_constants
from .. import INIT_DOTENV, connect, version
from ..constants.logs import (
    LOG_LEVELS_STR,
    REQUEST_ATTRS,
    REQUEST_ATTRS_DEFAULT,
    RESPONSE_ATTRS,
    RESPONSE_ATTRS_DEFAULT,
)
from ..logs import LOG
from ..setup_env import DEFAULT_ENV_FILE
from ..tools import json_dump
from . import (
    context,
    grp_account,
    grp_adapters,
    grp_assets,
    grp_certs,
    grp_enforcements,
    grp_folders,
    grp_openapi,
    grp_spaces,
    grp_system,
    grp_tools,
)

AX_ENV = os.environ.get("AX_ENV", "")

if os.path.isfile(INIT_DOTENV):
    DOT_INFO = f"Using existing .env file: {INIT_DOTENV!r}"
else:
    DOT_INFO = f"No .env file found, looking for {DEFAULT_ENV_FILE!r}"

PROTIPS: str = f"""

\b
{DOT_INFO}
AX_ENV={AX_ENV}
\b
Tips:
- All of the options listed above must be supplied BEFORE any commands or groups.
  - CORRECT: axonshell --log-console devices count
  - INCORRECT: axonshell devices count --log-console
- All values stored in a .env file will be treated as OS environment variables.
- Almost all options throughout axonshell have an associated OS environment variable.
- Use AX_ENV to point to a custom .env file:
  - bash: export AX_ENV=/path/to/.env  # for all commands in current shell
  - bash: AX_ENV=/path/to/.env axonshell tools shell  # for single commands
  - cmd.exe: SET AX_ENV="c:\\path\\to\\.env"
  - powershell: $AX_ENV = "c:\\path\\to\\.env"
- Multiple ways to specify AX_COOKIES and AX_HEADERS:
  - As CSV with , as delimiter: AX_COOKIES="key1=value1,key2=value2,key3=value4"
  - As CSV with ; as delimiter: AX_COOKIES="semi:key1=value1;key2=value2;key3=value4"
  - As JSON str: AX_HEADERS='json:{{"key1": "value1", "key2": "value2"}}'
- Use AX_URL, AX_KEY, AX_SECRET, AX_CREDENTIALS to specify credentials
"""
CF = cf_constants.CLIENT_DESC


@click.group(
    cls=context.AliasedGroup,
    context_settings=context.CONTEXT_SETTINGS,
    epilog=PROTIPS,
)
@click.option(
    "--quiet/--no-quiet",
    "-q/-nq",
    "quiet",
    default=False,
    help="Silence most green & blue output.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cookie",
    "-cook",
    "cookies",
    help="Additional cookies to supply with every request",
    cls=context.DictOption,
)
@click.option(
    "--header",
    "-head",
    "headers",
    help="Additional headers to supply with every request",
    cls=context.DictOption,
)
@click.option(
    "--cf-url",
    "-cfu",
    "cf_url",
    help=f"{CF}URL to use in cloudflared commands, will fallback to url if not supplied",
    default=None,
    envvar=["CF_URL", "AX_URL"],
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-token",
    "-cft",
    "cf_token",
    help=f"{CF}token supplied by user, will be checked for validity if not empty",
    default=None,
    envvar="CF_TOKEN",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-run/--no-cf-run",
    "-cfr/-ncfr",
    "cf_run",
    help=(
        f"{CF}If no token supplied or in OS env vars, try to get token from cloudflared commands"
    ),
    default=cf_constants.CLIENT_RUN,
    envvar="CF_RUN",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-run-access/--no-cf-run-access",
    "-cfrac/-ncfrac",
    "cf_run_access",
    help=f"{CF}If run is True, try to get token from `access token` command",
    default=cf_constants.FLOW_RUN_ACCESS,
    envvar="CF_RUN_ACCESS",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-run-login/--no-cf-run-login",
    "-cfrlc/-ncfrlc",
    "cf_run_login",
    help=(
        f"{CF}If run is True and no token returned from `access token` command, "
        f"try to get token from `access login` command"
    ),
    envvar="CF_RUN_LOGIN",
    default=cf_constants.FLOW_RUN_LOGIN,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-path",
    "-cfp",
    "cf_path",
    help=f"{CF}Path to cloudflared binary to run, can be full path or path in OS env var $PATH",
    default=cf_constants.CF_PATH,
    envvar="CF_PATH",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-timeout-access",
    "-cfta",
    "cf_timeout_access",
    help=f"{CF}Timeout for `access token` command in seconds",
    default=cf_constants.TIMEOUT_ACCESS,
    type=click.INT,
    envvar="CF_TIMEOUT_ACCESS",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-timeout-login",
    "-cftl",
    "cf_timeout_login",
    help=f"{CF}Timeout for `access login` command in seconds",
    default=cf_constants.TIMEOUT_LOGIN,
    type=click.INT,
    envvar="CF_TIMEOUT_LOGIN",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-error/--no-cf-error",
    "-cfe/-ncfe",
    "cf_error",
    help=f"{CF}Raise error if an invalid token is found or no token can be found",
    default=cf_constants.CLIENT_ERROR,
    envvar="CF_ERROR",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-error-access/--no-cf-error-access",
    "-cfeac/-ncfeac",
    "cf_error_access",
    help=f"{CF}Raise exc if `access token` command fails and login is False",
    default=cf_constants.FLOW_ERROR,
    envvar="CF_ERROR_ACCESS",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-error-login/--no-cf-error-login",
    "-cfel/-ncfel",
    "cf_error_login",
    help=f"{CF}Raise exc if `access login` command fails",
    default=cf_constants.FLOW_ERROR,
    envvar="CF_ERROR_LOGIN",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-echo/--no-cf-echo",
    "-cfec/-ncfec",
    "cf_echo",
    help=f"{CF}Echo commands and results to STDERR",
    default=cf_constants.FLOW_ECHO,
    envvar="CF_ECHO",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cf-echo-verbose/--no-cf-echo-verbose",
    "-cfev/-ncfev",
    "cf_echo_verbose",
    help=f"{CF}Echo more stuff to STDERR",
    default=cf_constants.FLOW_ECHO_VERBOSE,
    envvar="CF_ECHO_VERBOSE",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-package",
    "-lvlpkg",
    "log_level_package",
    default=connect.LOG_LEVEL_PACKAGE,
    help="Logging level to use for entire package.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-http",
    "-lvlhttp",
    "log_level_http",
    default=connect.Http.LOG_LEVEL,
    help="Logging level to use for http client.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-auth",
    "-lvlauth",
    "log_level_auth",
    default=connect.LOG_LEVEL_AUTH,
    help="Logging level to use for auth client.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-api",
    "-lvlapi",
    "log_level_api",
    default=connect.LOG_LEVEL_API,
    help="Logging level to use for API models.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-endpoints",
    "-lvlep",
    "log_level_endpoints",
    default=connect.LOG_LEVEL_ENDPOINTS,
    help="Logging level to use for API endpoints.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-console",
    "-lvlcon",
    "log_level_console",
    default=connect.LOG_LEVEL_CONSOLE,
    help="Logging level to use for console output.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-file",
    "-lvlfile",
    "log_level_file",
    default=connect.LOG_LEVEL_FILE,
    help="Logging level to use for file output.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-request-attrs",
    "-reqattr",
    "log_request_attrs",
    help="Log http client request attributes (multiples)",
    default=REQUEST_ATTRS_DEFAULT,
    multiple=True,
    type=click.Choice(REQUEST_ATTRS),
    show_envvar=True,
)
@click.option(
    "--log-response-attrs",
    "-respattr",
    "log_response_attrs",
    default=RESPONSE_ATTRS_DEFAULT,
    help="Log http client response attributes (multiples)",
    multiple=True,
    type=click.Choice(RESPONSE_ATTRS),
    show_envvar=True,
)
@click.option(
    "--log-request-body",
    "-reqbody",
    "log_request_body",
    default=False,
    help="Log http client request body.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--log-response-body",
    "-respbody",
    "log_response_body",
    help="Log http client response body.",
    default=False,
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--log-body-lines",
    "-lbl",
    "log_body_lines",
    default=connect.Http.LOG_BODY_LINES,
    help="Number of lines to log from request/response body.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-hide-secrets/--no-log-hide-secrets",
    "-lhs/-nlhs",
    "log_hide_secrets",
    default=True,
    help="Enable hiding of secrets in log output",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-console/--no-log-console",
    "-c/-nc",
    "log_console",
    default=False,
    help="Enable logging to STDERR.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--log-file/--no-log-file",
    "-f/-nf",
    "log_file",
    default=True,
    help="Enable logging to -fn/--log-file-name in -fp/--log-file-path.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--log-file-rotate/--no-log-file-rotate",
    "-fr/-nfr",
    "log_file_rotate",
    default=True,
    help="Force the log file to rotate.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--log-file-name",
    "-fn",
    "log_file_name",
    metavar="FILENAME",
    default=connect.LOG_FILE_NAME,
    help="Log file to save logs to if -f/--log-file supplied.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-token",
    "-fp",
    "log_file_path",
    metavar="PATH",
    default=connect.LOG_FILE_PATH,
    help="Directory to use for -fn/--log-file-name (Defaults to current directory).",
    show_envvar=True,
)
@click.option(
    "--log-file-max-mb",
    "-fmb",
    "log_file_max_mb",
    default=connect.LOG_FILE_MAX_MB,
    help="Rollover -fn/--log-file-name at this many megabytes.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-max-files",
    "-fmf",
    "log_file_max_files",
    default=connect.LOG_FILE_MAX_FILES,
    help="Keep this many rollover logs.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-hide-secrets/--no-log-hide-secrets",
    "-lhs/-nlhs",
    "log_hide_secrets",
    default=True,
    help="Enable hiding of secrets in log output",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-http-max/--no-log-http-max",
    "-lmax/-nlmax",
    "log_http_max",
    default=connect.Connect.LOG_HTTP_MAX,
    help=f"Shortcut to include_output http logging - overrides: {connect.Connect.HTTP_MAX_CLI}",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--proxy",
    "-p",
    "proxy",
    default="",
    help="Proxy to use to connect to Axonius.",
    metavar="PROXY",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cert-client-both",
    "-ccb",
    "cert_client_both",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to client SSL certificate and private key in one file for mutual TLS.",
    metavar="PATH",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cert-client-cert",
    "-ccc",
    "cert_client_cert",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to client SSL certificate for mutual TLS.",
    metavar="PATH",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cert-client-key",
    "-cck",
    "cert_client_key",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to client SSL private key for mutual TLS",
    metavar="PATH",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--certpath",
    "-cp",
    "certpath",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to SSL certificate for verifying the certificate offered by Axonius.",
    metavar="PATH",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--certverify",
    "-cv",
    "certverify",
    default=False,
    help=(
        "Perform SSL Certificate Verification (will fail if cert is self-signed"
        " or not signed by a system CA)."
    ),
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--no-certwarn",
    "-ncw",
    "certwarn",
    default=True,
    help="Disable warnings for self-signed SSL certificates.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--no-wraperror",
    "-nw",
    "wraperror",
    default=True,
    help="Show the full traceback of exceptions instead of a wrapped error.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--timeout-connect",
    "-tc",
    "timeout_connect",
    default=connect.Http.CONNECT_TIMEOUT,
    help="Seconds to wait for connections to API",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--timeout-response",
    "-tr",
    "timeout_response",
    default=connect.Http.RESPONSE_TIMEOUT,
    help="Seconds to wait for responses from API",
    type=click.INT,
    show_default=True,
)
@click.option(
    "--credentials/--keys",
    "-creds/-keys",
    "credentials",
    default=False,
    help="Treat key as Username and secret as password",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.version_option(version.__version__)
@context.pass_context
@click.pass_context
def cli(click_ctx, ctx, quiet, **kwargs):
    """Command line interface for the Axonius API Client."""
    # noinspection PyBroadException
    try:
        cli_args = sys.argv
    except Exception:  # pragma: no cover
        cli_args = "No sys.argv!"
    LOG.debug(f"sys.argv: {json_dump(cli_args)}")
    LOG.debug(f"kwargs: {json_dump(kwargs)}")
    ctx._click_ctx = click_ctx
    ctx.QUIET = quiet
    # noinspection PyProtectedMember
    ctx._connect_args.update(kwargs)


GROUPS: t.List[click.Group] = [
    grp_adapters.adapters,
    grp_assets.devices,
    grp_assets.users,
    grp_assets.vulnerabilities,
    grp_system.system,
    grp_tools.tools,
    grp_openapi.openapi,
    grp_certs.certs,
    grp_enforcements.enforcements,
    grp_spaces.spaces,
    grp_folders.folders,
    grp_account.account,
]

for grp in GROUPS:
    cli.add_command(grp)
