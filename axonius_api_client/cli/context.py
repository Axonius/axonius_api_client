# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import atexit
import csv
import functools
import os
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

KV_TMPL = "{}: {}".format

MAX_LEN = 30000
MAX_STR = "...TRIMMED - {} items over max cell length {}".format


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
        "-u",
        required=True,
        help="URL of Axonius instance.",
        metavar="URL",
        prompt="URL of Axonius instance",
        show_envvar=True,
    )
    @click.option(
        "--key",
        "-k",
        required=True,
        help="API Key of user in Axonius instance.",
        metavar="KEY",
        prompt="API Key of user in Axonius instance",
        hide_input=True,
        show_envvar=True,
    )
    @click.option(
        "--secret",
        "-s",
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
        "-xf",
        default="",
        help="Export to a file in export-path instead of printing to STDOUT.",
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-path",
        "-xp",
        default=format(tools.path(obj=os.getcwd())),
        help="Path to create --export-file in.",
        type=click.Path(exists=False, resolve_path=True),
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-format",
        "-xt",
        default="json",
        help="Format to use for STDOUT or export-file.",
        type=click.Choice(["csv", "json"]),
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-overwrite/--no-export-overwrite",
        "-xo/-nxo",
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


class SplitEquals(click.ParamType):
    """Pass."""

    name = "split_equals"

    def convert(self, value, param, ctx):
        """Pass."""
        split = value.split("=", 1)

        if len(split) != 2:
            msg = "Need an '=' in --{p} with value {v!r}"
            msg = msg.format(p=param.name, v=value)
            self.fail(msg, param, ctx)

        return [x.strip() for x in split]


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


def json_from_stream(ctx, stream, src):
    """Pass."""
    stream_name = getattr(stream, "name", format(stream))
    if stream.isatty():
        # its STDIN with no input
        msg = "No input provided on {s} for {src}"
        msg = msg.format(s=stream_name, src=src)
        ctx.echo_error(msg)

    # its STDIN with input or a file
    content = stream.read()
    msg = "Read {n} bytes from {s} for {src}"
    msg = msg.format(n=len(content), s=stream_name, src=src)
    ctx.echo_ok(msg)

    content = content.strip()

    if not content:
        msg = "Empty content supplied in {s} for {src}"
        msg = msg.format(s=stream_name, src=src)
        ctx.echo_error(msg)

    with exc_wrap(wraperror=ctx.wraperror):
        content = tools.json_load(obj=content)

    msg = "Loaded JSON content from {src} as {t} with length of {n}"
    msg = msg.format(t=type(content).__name__, src=src, n=len(content))
    ctx.echo_ok(msg)

    return content


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


def to_json(ctx, raw_data, **kwargs):
    """Pass."""
    return tools.json_dump(obj=raw_data)


def is_simple(o):
    """Is simple."""
    return isinstance(o, tools.SIMPLE) or o is None


def is_list(o):
    """Is simple."""
    return isinstance(o, tools.LIST)


def is_los(o):
    """Is simple or list of simples."""
    return is_simple(o) or (is_list(o) and all([is_simple(x) for x in o]))


def is_dos(o):
    """Is dict with simple or list of simple values."""
    return isinstance(o, dict) and all([is_los(v) for v in o.values()])


def obj_to_csv(ctx, raw_data, **kwargs):
    """Pass."""
    raw_data = tools.listify(obj=raw_data, dictkeys=False)
    rows = []

    for raw_row in raw_data:
        row = {}
        rows.append(row)
        for raw_key, raw_value in raw_row.items():

            if is_los(raw_value):
                row[raw_key] = join_cr(raw_value, is_cell=True)
                continue

            if is_list(raw_value) and all([is_dos(x) for x in raw_value]):
                values = {}

                for raw_item in raw_value:
                    for k, v in raw_item.items():
                        new_key = "{}.{}".format(raw_key, k)

                        values[new_key] = values.get(new_key, [])

                        values[new_key] += tools.listify(v, dictkeys=False)

                for k, v in values.items():
                    row[k] = join_cr(v, is_cell=True)

                continue

            msg = "Data of type {t} is too complex for CSV format"
            msg = msg.format(t=type(raw_value).__name__)
            row[raw_key] = msg

    return dictwriter(rows=rows)


def check_empty(
    ctx, this_data, prev_data, value_type, value, objtype, known_cb, known_cb_key
):
    """Pass."""
    if value in tools.EMPTY:
        return

    value = tools.join_comma(obj=value, empty=False)
    if not this_data:
        msg = "Valid {objtype}:{valid}\n"
        msg = msg.format(
            valid=tools.join_cr(known_cb(**{known_cb_key: prev_data})), objtype=objtype
        )
        ctx.echo_error(msg, abort=False)

        msg = "No {objtype} found when searching by {value_type}: {value}"
        msg = msg.format(objtype=objtype, value_type=value_type, value=value)
        ctx.echo_error(msg)

    msg = "Found {cnt} {objtype} by {value_type}: {value}"
    msg = msg.format(
        objtype=objtype, cnt=len(this_data), value_type=value_type, value=value
    )
    ctx.echo_ok(msg)


def join_kv(obj, indent="  "):
    """Pass."""
    items = [KV_TMPL(k, v) for k, v in obj.items()]
    return tools.join_cr(obj=items, indent=indent)


def join_tv(obj):
    """Pass."""
    items = [KV_TMPL(v["title"], v["value"]) for k, v in obj.items()]
    return join_cr(items)


def join_cr(obj, is_cell=False):
    """Pass."""
    stro = tools.join_cr(obj=obj, pre=False, post=False, indent="")

    if is_cell and len(stro) >= MAX_LEN:
        stro = tools.join_cr([stro[:MAX_LEN], MAX_STR(len(obj), MAX_LEN)])

    return stro


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
        **kwargs,
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
