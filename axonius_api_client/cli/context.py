# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import atexit
import csv
import functools
import os
import pdb  # noqa
import readline
import rlcompleter
import sys
import warnings

import click
import dotenv
import requests

from .. import connect, tools
from ..tools import json_reload as jdump

HISTPATH = os.path.expanduser("~")
HISTFILE = ".python_history"
CONTEXT_SETTINGS = {"auto_envvar_prefix": "AX"}
REASON = "Export format {ef!r} is unsupported!  Must be one of: {sf}"
QUOTING = csv.QUOTE_NONNUMERIC


def load_dotenv():
    """Pass."""
    ax_env = os.environ.get("AX_ENV", "")

    if ax_env:
        path = tools.path(obj=ax_env)
    else:
        path = tools.path(obj=os.getcwd()) / ".env"

    dotenv.load_dotenv(format(path))


def connect_options(func):
    """Combine commonly appearing @click.option decorators."""
    #
    @click.option(
        "--url",
        required=True,
        help="URL of Axonius instance.",
        metavar="URL",
        prompt="URL of Axonius instance",
        show_envvar=True,
    )
    @click.option(
        "--key",
        required=True,
        help="API Key of user in Axonius instance.",
        metavar="KEY",
        prompt="API Key of user in Axonius instance",
        hide_input=True,
        show_envvar=True,
    )
    @click.option(
        "--secret",
        required=True,
        help="API Secret of user in Axonius instance.",
        metavar="SECRET",
        prompt="API Secret of user in Axonius instance",
        hide_input=True,
        show_envvar=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def export_options(func):
    """Combine commonly appearing @click.option decorators."""
    #
    # FUTURE: error if os.path.sep in value
    @click.option(
        "--export-file",
        default="",
        help="Export to a file in export-path instead of printing to STDOUT.",
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-path",
        default=format(tools.path(obj=os.getcwd())),
        help="Path to create --export-file in.",
        type=click.Path(exists=False, resolve_path=True),
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-format",
        default="json",
        help="Format to use for STDOUT or export-file.",
        type=click.Choice(["csv", "json"]),
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-overwrite/--no-export-overwrite",
        default=False,
        help="Overwrite export-file if exists.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class exc_wrap(object):
    """Pass."""

    def __init__(self, wraperror=True):
        """Pass."""
        self.wraperror = wraperror

    def __enter__(self):
        """Pass."""
        return self

    def __exit__(self, exc, value, traceback):
        """Pass."""
        if value and self.wraperror and not isinstance(value, SystemExit):
            msg = "WRAPPED EXCEPTION: {c.__module__}.{c.__name__}\n{v}"
            msg = msg.format(c=value.__class__, v=value)
            Context.echo_error(msg)


# FIELD_FORMAT = "fields need to be in the format of adapter_name:field_name"
# DEFAULT_FIELD = "generic:{field}"

# def cb_fields(ctx, param, value):
#     """Pass."""
#     fields = {}

#     if not value:
#         return fields

#     value = value if isinstance(value, tools.LIST) else [value]

#     for x in value:
#         if ":" not in x:
#             x = DEFAULT_FIELD.format(field=x)

#         try:
#             adapter, field = x.split(":")
#             adapter, field = adapter.lower().strip(), field.lower().strip()
#         except ValueError:
#             raise click.BadParameter(FIELD_FORMAT)

#         fields[adapter] = fields.get(adapter, [])

#         if field not in fields[adapter]:
#             fields[adapter].append(field)

#     return fields


def dictwriter(rows, stream=None, headers=None, quoting=QUOTING, **kwargs):
    """Pass."""
    fh = stream or tools.six.StringIO()

    headers = headers or []

    if not headers:
        for row in rows:
            headers += [k for k in row if k not in headers]

    writer = csv.DictWriter(fh, fieldnames=headers, quoting=quoting, **kwargs)

    writer.writeheader()

    for row in rows:
        writer.writerow(row)

    return fh.getvalue()


def write_hist_file():
    """Pass."""
    histpath = tools.pathlib.Path(HISTPATH)
    histfile = histpath / HISTFILE

    histpath.mkdir(mode=0o700, exist_ok=True)
    histfile.touch(mode=0o600, exist_ok=True)

    readline.write_history_file(format(histfile))


def register_readline(shellvars=None):
    """Pass."""
    shellvars = shellvars or {}

    histpath = tools.pathlib.Path(HISTPATH)
    histfile = histpath / HISTFILE

    histpath.mkdir(mode=0o700, exist_ok=True)
    histfile.touch(mode=0o600, exist_ok=True)

    try:
        readline.read_history_file(format(histfile))
        atexit.register(write_hist_file)

        readline.set_completer(rlcompleter.Completer(shellvars).complete)

        readline_doc = getattr(readline, "__doc__", "")
        is_libedit = readline_doc and "libedit" in readline_doc

        pab = "bind ^I rl_complete" if is_libedit else "tab: complete"
        readline.parse_and_bind(pab)

    except Exception as exc:
        msg = "Unable to register history and autocomplete:\n{}".format(exc)
        Context.echo_error(msg, abort=False)


def spawn_shell(shellvars=None):
    """Pass."""
    import code

    shellvars = shellvars or {}
    shellvars.setdefault("jdump", jdump)
    register_readline(shellvars)

    code.interact(local=shellvars)


class Context(object):
    """Pass."""

    OK_ARGS = {"fg": "green", "bold": True, "err": True}
    OK_TMPL = "** {msg}"

    WARN_ARGS = {"fg": "yellow", "bold": True, "err": True}
    WARN_TMPL = "** WARNING: {msg}"

    ERROR_ARGS = {"fg": "red", "bold": True, "err": True}
    ERROR_TMPL = "** ERROR: {msg}"

    SSLWARN_MSG = (
        "Unverified HTTPS request! Set AX_CERT environment variable or "
        "--cert option to the path of a CA bundle!"
    )
    SSLWARN_CLS = requests.urllib3.exceptions.InsecureRequestWarning

    def __init__(self):
        """Pass."""
        self.obj = None
        self._click_ctx = None
        self._connect_args = {}
        self._export_args = {}

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return format(self.obj)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    def export(self, data, export_file=None, export_path=None, export_overwrite=False):
        """Pass."""
        if not export_file:
            click.echo(data)
            return

        export_path = export_path or os.getcwd()

        path = tools.path(obj=export_path)
        path.mkdir(mode=0o700, parents=True, exist_ok=True)

        full_path = path / export_file

        mode = "overwritten" if full_path.exists() else "created"

        if full_path.exists() and not export_overwrite:
            msg = "Export file {p} already exists and export-overwite is False!"
            msg = msg.format(p=full_path)
            self.echo_error(msg=msg)

        full_path.touch(mode=0o600)

        with full_path.open(mode="w", newline="") as fh:
            fh.write(data)

        msg = "Exported file {p!r} {mode}!"
        msg = msg.format(p=format(full_path), mode=mode)
        self.echo_ok(msg)

    @classmethod
    def echo_ok(cls, msg):
        """Pass."""
        click.secho(cls.OK_TMPL.format(msg=msg), **cls.OK_ARGS)

    @classmethod
    def echo_error(cls, msg, abort=True):
        """Pass."""
        click.secho(cls.ERROR_TMPL.format(msg=msg), **cls.ERROR_ARGS)
        if abort:
            sys.exit(1)

    @classmethod
    def echo_warn(cls, msg):
        """Pass."""
        click.secho(cls.WARN_TMPL.format(msg=msg), **cls.WARN_ARGS)

    @property
    def wraperror(self):
        """Pass."""
        return self._connect_args.get("wraperror", True)

    def start_client(self, url, key, secret, **kwargs):
        """Pass."""
        if not getattr(self, "obj", None):
            connect_args = {}
            connect_args.update(self._connect_args)
            connect_args.update(kwargs)
            connect_args["url"] = url
            connect_args["key"] = key
            connect_args["secret"] = secret

            with exc_wrap(wraperror=self.wraperror):
                self.obj = connect.Connect(**connect_args)

                with warnings.catch_warnings(record=True) as caught_warnings:
                    self.obj.start()

                for caught_warning in caught_warnings:
                    wmsg = caught_warning.message
                    is_ssl = isinstance(wmsg, self.SSLWARN_CLS)
                    wmsg = self.SSLWARN_MSG if is_ssl else wmsg
                    wmsg = format(wmsg)
                    self.echo_warn(wmsg)

            # warnings suck.
            warnings.simplefilter("ignore", self.SSLWARN_CLS)

            self.echo_ok(msg=self.obj)

        return self.obj

    def handle_export(
        self,
        raw_data,
        formatters,
        export_format,
        export_file,
        export_path,
        export_overwrite,
        ctx=None,
        reason=REASON,
        **kwargs
    ):
        """Pass."""
        if export_format not in formatters:
            self.echo_error(msg=reason.format(ef=export_format, sf=list(formatters)))

        with exc_wrap(wraperror=self.wraperror):
            data = formatters[export_format](
                ctx=ctx or self, raw_data=raw_data, **kwargs
            )

        self.export(
            data=data,
            export_file=export_file,
            export_path=export_path,
            export_overwrite=export_overwrite,
        )


pass_context = click.make_pass_decorator(Context, ensure=True)
