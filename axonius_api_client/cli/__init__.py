# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import constants, version
from . import cli_constants, click_ext, context, grp_adapters, grp_objects, grp_tools

# FUTURE: grp_enforcements
# FUTURE: wrap json datasets with objtype info
# FUTURE: --verbose/--no-verbose to silence echo_ok
# FUTURE: --warning/--no-warning to silence echo_warn
# FUTURE: way to only import cli stuffs so package doesnt see unless needed
# FUTURE: add cert_human logic
# FUTURE: prompt does not use CR when re-prompting on empty var with hide_input=False
# FUTURE: add doc links


@click.group(
    cls=click_ext.AliasedGroup,
    context_settings=cli_constants.CONTEXT_SETTINGS,
    epilog="""
All of the options listed above must be supplied BEFORE any commands or groups.
""",
)
@click.option(
    "--log-level-package",
    "-lvlpkg",
    "log_level_package",
    default=constants.LOG_LEVEL_PACKAGE,
    help="Logging level to use for entire package.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-http",
    "-lvlhttp",
    "log_level_http",
    default=constants.LOG_LEVEL_HTTP,
    help="Logging level to use for http client.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-auth",
    "-lvlauth",
    "log_level_auth",
    default=constants.LOG_LEVEL_AUTH,
    help="Logging level to use for auth client.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-api",
    "-lvlapi",
    "log_level_api",
    default=constants.LOG_LEVEL_API,
    help="Logging level to use for api clients.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-console",
    "-lvlcon",
    "log_level_console",
    default=constants.LOG_LEVEL_CONSOLE,
    help="Logging level to use for console output.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-file",
    "-lvlfile",
    "log_level_file",
    default=constants.LOG_LEVEL_FILE,
    help="Logging level to use for file output.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-request-attrs-verbose/--log-request-attrs-brief",
    "-reqv/-reqb",
    "log_request_attrs",
    default=None,
    help="Log http client verbose or brief request attributes.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--log-response-attrs-verbose/--log-response-attrs-brief",
    "-respv/-respb",
    "log_response_attrs",
    default=None,
    help="Log http client verbose or brief response attributes.",
    is_flag=True,
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
    "--log-console",
    "-c",
    "log_console",
    default=False,
    help="Enable logging to STDERR.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--log-file",
    "-f",
    "log_file",
    default=False,
    help="Enable logging to -fn/--log-file-name in -fp/--log-file-path.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--log-file-name",
    "-fn",
    "log_file_name",
    metavar="FILENAME",
    default=constants.LOG_FILE_NAME,
    help="Log file to save logs to if -f/--log-file supplied.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-path",
    "-fp",
    "log_file_path",
    metavar="PATH",
    default=constants.LOG_FILE_PATH,
    help="Directory to use for -fn/--log-file-name (Defaults to CWD).",
    show_envvar=True,
)
@click.option(
    "--log-file-max-mb",
    "-fmb",
    "log_file_max_mb",
    default=constants.LOG_FILE_MAX_MB,
    help="Rollover -fn/--log-file-name at this many megabytes.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-max-files",
    "-fmf",
    "log_file_max_files",
    default=constants.LOG_FILE_MAX_FILES,
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
    proxy,
    certpath,
    certverify,
    certwarn,
    wraperror,
):
    """Command line interface for the Axonius API Client."""
    ctx._click_ctx = click_ctx
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
    ctx._connect_args["certpath"] = certpath
    ctx._connect_args["certverify"] = certverify
    ctx._connect_args["certwarn"] = certwarn
    ctx._connect_args["wraperror"] = wraperror


cli.add_command(grp_adapters.adapters)
cli.add_command(grp_objects.devices)
cli.add_command(grp_objects.users)
cli.add_command(grp_tools.tools)
