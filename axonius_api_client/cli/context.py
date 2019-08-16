# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import csv
import functools
import json
import os
import sys
import warnings

import click
import dotenv
import requests
import six

from .. import connect, tools

AX_DOTENV = os.environ.get("AX_DOTENV", "")
CWD_PATH = tools.resolve_path(os.getcwd())
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


def load_dotenv():
    """Pass."""
    path = tools.resolve_path(AX_DOTENV) if AX_DOTENV else CWD_PATH / ".env"
    dotenv.load_dotenv(format(path))


def ok(msg, exit=None):
    """Pass."""
    click.secho(OK_TMPL.format(msg=msg), **OK_ARGS)
    if exit is not None:
        sys.exit(exit)


def error(msg, exit=1):
    """Pass."""
    click.secho(ERROR_TMPL.format(msg=msg), **ERROR_ARGS)
    if exit is not None:
        sys.exit(exit)


def warn(msg, exit=None):
    """Pass."""
    click.secho(WARN_TMPL.format(msg=msg), **WARN_ARGS)
    if exit is not None:
        sys.exit(exit)


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


class Context(object):
    """Pass."""

    CSV_QUOTING = csv.QUOTE_NONNUMERIC

    def __init__(self):
        """Pass."""
        self.obj = None
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

        path = tools.resolve_path(export_path)
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
        full_path.write_text(data)

        msg = "Export file {p!r} {mode}!"
        msg = msg.format(p=format(full_path), mode=mode)
        self.echo_ok(msg)

    def echo_ok(self, msg, exit=None):
        """Pass."""
        ok(msg=msg, exit=exit)

    def echo_error(self, msg, exit=1):
        """Pass."""
        error(msg=msg, exit=exit)

    def echo_warn(self, msg, exit=None):
        """Pass."""
        warn(msg=msg, exit=exit)

    @staticmethod
    def to_json(data, indent=2):
        """Pass."""
        return json.dumps(data, indent=indent)

    @classmethod
    def dicts_to_csv(cls, rows, headers=None):
        """Pass."""
        if headers is None:
            headers = []
            for row in rows:
                for key in row:
                    if key not in headers:
                        headers.append(key)

        stream = six.StringIO()
        writer = csv.DictWriter(stream, quoting=cls.CSV_QUOTING, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return stream.getvalue()

    def _start_client(self):
        """Pass."""
        wraperror = self._connect_args.get("wraperror", True)
        with warnings.catch_warnings(record=True) as caught_warnings:
            try:
                self.obj.start()
            except Exception as exc:
                if wraperror:
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

    def start_client(self, url, key, secret):
        """Pass."""
        if not getattr(self, "obj", None):
            wraperror = self._connect_args.get("wraperror", True)
            connect_args = {}
            connect_args.update(self._connect_args)
            connect_args["url"] = url
            connect_args["key"] = key
            connect_args["secret"] = secret
            try:
                self.obj = connect.Connect(**connect_args)
            except Exception as exc:
                if wraperror:
                    self.echo_error(format(exc))
                raise

            self._start_client()
            self.echo_ok(msg=self.obj)
        return self.obj


pass_context = click.make_pass_decorator(Context, ensure=True)
