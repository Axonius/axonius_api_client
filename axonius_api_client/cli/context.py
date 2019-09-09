# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import functools
import os
import sys
import warnings

import click
import dotenv
import requests

from .. import connect, tools

AX_DOTENV = os.environ.get("AX_DOTENV", "")
CWD_PATH = tools.path(obj=os.getcwd())
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

CONTEXT_SETTINGS = {"auto_envvar_prefix": "AX"}

FIELD_FORMAT = "fields need to be in the format of adapter_name:field_name"
DEFAULT_FIELD = "generic:{field}"


def jdump(obj, **kwargs):
    """JSON dump utility."""
    print(tools.json_reload(obj, **kwargs))


def load_dotenv():
    """Pass."""
    path = tools.path(obj=AX_DOTENV) if AX_DOTENV else CWD_PATH / ".env"
    dotenv.load_dotenv(format(path))


def ok(msg):
    """Pass."""
    click.secho(OK_TMPL.format(msg=msg), **OK_ARGS)


def error(msg):
    """Pass."""
    click.secho(ERROR_TMPL.format(msg=msg), **ERROR_ARGS)


def warn(msg):
    """Pass."""
    click.secho(WARN_TMPL.format(msg=msg), **WARN_ARGS)


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
        default=format(CWD_PATH),
        help="Path to create --export-file in.",
        type=click.Path(exists=False, resolve_path=True),
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-format",
        default="json",
        help="Format to use for STDOUT or export-file.",
        # type=click.Choice(["csv", "json"]),
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


def cb_fields(ctx, param, value):
    """Pass."""
    fields = {}

    if not value:
        return fields

    value = value if isinstance(value, tools.LIST) else [value]

    for x in value:
        if ":" not in x:
            x = DEFAULT_FIELD.format(field=x)

        try:
            adapter, field = x.split(":")
            adapter, field = adapter.lower().strip(), field.lower().strip()
        except ValueError:
            raise click.BadParameter(FIELD_FORMAT)

        fields[adapter] = fields.get(adapter, [])

        if field not in fields[adapter]:
            fields[adapter].append(field)

    return fields


class Context(object):
    """Pass."""

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

    def export(
        self, data, export_file="", export_path=os.getcwd(), export_overwrite=False
    ):
        """Pass."""
        if not export_file:
            click.echo(data)
            return

        path = tools.path(obj=export_path)
        path.mkdir(mode=0o700, parents=True, exist_ok=True)

        full_path = path / export_file

        mode = "created"

        if full_path.exists():
            if not export_overwrite:
                msg = "Export file {p} already exists and export-overwite is False!"
                msg = msg.format(p=full_path)
                self.echo_error(msg=msg)

            mode = "overwritten"

        full_path.touch(mode=0o600)

        with full_path.open(mode="w", newline="") as fh:
            fh.write(data)

        msg = "Export file {p!r} {mode}!"
        msg = msg.format(p=format(full_path), mode=mode)
        self.echo_ok(msg)

    def echo_ok(self, msg):
        """Pass."""
        ok(msg=msg)

    def echo_error(self, msg, abort=True):
        """Pass."""
        error(msg=msg)
        if abort:
            sys.exit(1)

    def echo_warn(self, msg, abort=False):
        """Pass."""
        warn(msg=msg)
        if abort:
            sys.exit(1)

    @staticmethod
    def to_json(ctx, raw_data, **kwargs):
        """Pass."""
        return tools.json_dump(obj=raw_data, **kwargs)

    @staticmethod
    def to_csv(ctx, raw_data, **kwargs):
        """Pass."""
        kwargs.setdefault("compress", True)
        kwargs.setdefault("stream_value", True)
        return tools.csv.cereal(raw_data, **kwargs)

    @property
    def wraperror(self):
        """Pass."""
        return self._connect_args.get("wraperror", True)

    def _start_client(self):
        """Pass."""
        with warnings.catch_warnings(record=True) as caught_warnings:
            try:
                self.obj.start()
            except Exception as exc:
                if self.wraperror:
                    self.echo_error(format(exc))
                raise
            for caught_warning in caught_warnings:
                if isinstance(caught_warning.message, SSLWARN_CLS):
                    warn(SSLWARN_MSG)
                else:
                    msg = format(caught_warning.message)
                    warn(msg)
        # warnings suck.
        warnings.simplefilter("ignore", SSLWARN_CLS)

    def start_client(self, url, key, secret, **kwargs):
        """Pass."""
        if not getattr(self, "obj", None):
            connect_args = {}
            connect_args.update(self._connect_args)
            connect_args.update(kwargs)
            connect_args["url"] = url
            connect_args["key"] = key
            connect_args["secret"] = secret
            try:
                self.obj = connect.Connect(**connect_args)
            except Exception as exc:
                if self.wraperror:
                    self.echo_error(format(exc))
                raise

            self._start_client()
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
        **kwargs
    ):
        """Pass."""
        if export_format in formatters:
            data = formatters[export_format](
                ctx=ctx or self, raw_data=raw_data, **kwargs
            )
        else:
            msg = "Export format {f!r} is unsupported! Must be one of: {sf}"
            msg = msg.format(f=export_format, sf=list(formatters.keys()))
            self.echo_error(msg=msg)

        self.export(
            data=data,
            export_file=export_file,
            export_path=export_path,
            export_overwrite=export_overwrite,
        )


pass_context = click.make_pass_decorator(Context, ensure=True)


def register_readline(shellvars=None):
    """Pass."""
    try:
        import atexit
        import os
        import readline
        import rlcompleter

        shellvars = shellvars or {}

        home = os.path.expanduser("~")
        histfile = ".python_history"
        histfile = os.path.join(home, histfile)

        if os.path.isfile(histfile):
            readline.read_history_file(histfile)

        if os.path.isdir(home):
            atexit.register(readline.write_history_file, histfile)

        readline.set_completer(rlcompleter.Completer(shellvars).complete)

        readline_doc = getattr(readline, "__doc__", "")

        if readline_doc is not None and "libedit" in readline_doc:
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")
    except Exception as exc:
        msg = "Unable to register history and autocomplete: {}".format(exc)
        print(msg)


def spawn_shell(shellvars=None):
    """Pass."""
    import code

    shellvars = shellvars or {}
    shellvars.setdefault("jdump", jdump)
    register_readline(shellvars)

    code.interact(local=shellvars)
