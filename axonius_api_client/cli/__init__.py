# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import sys

import click

from .. import version
from ..constants.api import TIMEOUT_CONNECT, TIMEOUT_RESPONSE
from ..constants.logs import (
    LOG_FILE_MAX_FILES,
    LOG_FILE_MAX_MB,
    LOG_FILE_NAME,
    LOG_FILE_PATH,
    LOG_LEVEL_API,
    LOG_LEVEL_AUTH,
    LOG_LEVEL_CONSOLE,
    LOG_LEVEL_FILE,
    LOG_LEVEL_HTTP,
    LOG_LEVEL_PACKAGE,
    LOG_LEVELS_STR,
    REQUEST_ATTR_MAP,
    RESPONSE_ATTR_MAP,
)
from ..logs import LOG
from . import context, grp_adapters, grp_assets, grp_system, grp_tools


@click.group(
    cls=context.AliasedGroup,
    context_settings=context.CONTEXT_SETTINGS,
    epilog="""
All of the options listed above must be supplied BEFORE any commands or groups.
""",
)
@click.option(
    "--quiet/--no-quiet",
    "-q/-nq",
    "quiet",
    default=False,
    help="Silence green text.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--header",
    "headers",
    default=[],
    help="Additional headers to use in all requests in the format of key=value (multiples)",
    show_envvar=True,
    show_default=True,
    multiple=True,
    type=context.SplitEquals(),
)
@click.option(
    "--log-level-package",
    "-lvlpkg",
    "log_level_package",
    default=LOG_LEVEL_PACKAGE,
    help="Logging level to use for entire package.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-http",
    "-lvlhttp",
    "log_level_http",
    default=LOG_LEVEL_HTTP,
    help="Logging level to use for http client.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-auth",
    "-lvlauth",
    "log_level_auth",
    default=LOG_LEVEL_AUTH,
    help="Logging level to use for auth client.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-api",
    "-lvlapi",
    "log_level_api",
    default=LOG_LEVEL_API,
    help="Logging level to use for api clients.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-console",
    "-lvlcon",
    "log_level_console",
    default=LOG_LEVEL_CONSOLE,
    help="Logging level to use for console output.",
    type=click.Choice(LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-file",
    "-lvlfile",
    "log_level_file",
    default=LOG_LEVEL_FILE,
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
    default=["size", "url"],
    multiple=True,
    type=click.Choice(list(REQUEST_ATTR_MAP) + ["all"]),
    show_envvar=True,
)
@click.option(
    "--log-response-attrs",
    "-respattr",
    "log_response_attrs",
    default=["size", "url", "status", "elapsed"],
    help="Log http client response attributes (multiples)",
    multiple=True,
    type=click.Choice(list(RESPONSE_ATTR_MAP) + ["all"]),
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
    "--log-file-name",
    "-fn",
    "log_file_name",
    metavar="FILENAME",
    default=LOG_FILE_NAME,
    help="Log file to save logs to if -f/--log-file supplied.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-path",
    "-fp",
    "log_file_path",
    metavar="PATH",
    default=LOG_FILE_PATH,
    help="Directory to use for -fn/--log-file-name (Defaults to current directory).",
    show_envvar=True,
)
@click.option(
    "--log-file-max-mb",
    "-fmb",
    "log_file_max_mb",
    default=LOG_FILE_MAX_MB,
    help="Rollover -fn/--log-file-name at this many megabytes.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-max-files",
    "-fmf",
    "log_file_max_files",
    default=LOG_FILE_MAX_FILES,
    help="Keep this many rollover logs.",
    type=click.INT,
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
    default=TIMEOUT_CONNECT,
    help="Seconds to wait for connections to API",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--timeout-response",
    "-tr",
    "timeout_response",
    default=TIMEOUT_RESPONSE,
    help="Seconds to wait for responses from API",
    type=click.INT,
    show_default=True,
)
@click.version_option(version.__version__)
@context.pass_context
@click.pass_context
def cli(
    click_ctx,
    ctx,
    log_level_package,
    log_level_http,
    log_level_auth,
    log_level_api,
    log_level_console,
    log_level_file,
    log_console,
    log_file,
    log_request_attrs,
    log_response_attrs,
    log_request_body,
    log_response_body,
    log_file_name,
    log_file_path,
    log_file_max_mb,
    log_file_max_files,
    cert_client_cert,
    cert_client_key,
    cert_client_both,
    proxy,
    certpath,
    certverify,
    certwarn,
    wraperror,
    timeout_connect,
    timeout_response,
    quiet,
    headers,
):
    """Command line interface for the Axonius API Client."""
    try:
        cli_args = sys.argv
    except Exception:
        cli_args = "No sys.argv!"

    LOG.debug(f"sys.argv: {cli_args}")
    ctx._click_ctx = click_ctx
    ctx.QUIET = quiet
    ctx._connect_args["log_level_package"] = log_level_package
    ctx._connect_args["log_level_http"] = log_level_http
    ctx._connect_args["log_level_auth"] = log_level_auth
    ctx._connect_args["log_level_api"] = log_level_api
    ctx._connect_args["log_level_console"] = log_level_console
    ctx._connect_args["log_level_file"] = log_level_file
    ctx._connect_args["log_console"] = log_console
    ctx._connect_args["log_file"] = log_file
    ctx._connect_args["log_request_attrs"] = log_request_attrs
    ctx._connect_args["log_response_attrs"] = log_response_attrs
    ctx._connect_args["log_request_body"] = log_request_body
    ctx._connect_args["log_response_body"] = log_response_body
    ctx._connect_args["log_file_name"] = log_file_name
    ctx._connect_args["log_file_path"] = log_file_path
    ctx._connect_args["log_file_max_mb"] = log_file_max_mb
    ctx._connect_args["log_file_max_files"] = log_file_max_files
    ctx._connect_args["proxy"] = proxy
    ctx._connect_args["cert_client_cert"] = cert_client_cert
    ctx._connect_args["cert_client_key"] = cert_client_key
    ctx._connect_args["cert_client_both"] = cert_client_both
    ctx._connect_args["certpath"] = certpath
    ctx._connect_args["certverify"] = certverify
    ctx._connect_args["certwarn"] = certwarn
    ctx._connect_args["wraperror"] = wraperror
    ctx._connect_args["timeout_connect"] = timeout_connect
    ctx._connect_args["timeout_response"] = timeout_response
    ctx._connect_args["headers"] = headers


cli.add_command(grp_adapters.adapters)
cli.add_command(grp_assets.devices)
cli.add_command(grp_assets.users)
cli.add_command(grp_system.system)
cli.add_command(grp_tools.tools)
