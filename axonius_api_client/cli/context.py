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

from .. import connect, tools, version

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


def ok(msg):
    """Pass."""
    click.secho(OK_TMPL.format(msg=msg), **OK_ARGS)


def error(msg, exit=True):
    """Pass."""
    click.secho(ERROR_TMPL.format(msg=msg), **ERROR_ARGS)
    if exit:
        sys.exit(1)


def warn(msg):
    """Pass."""
    click.secho(WARN_TMPL.format(msg=msg), **WARN_ARGS)


DEFAULTS = {
    "url": None,
    "key": None,
    "secret": None,
    "proxy": "",
    "certpath": None,
    "certverify": False,
    "certwarn": True,
    "wraperror": True,
    "verbose": True,
    "log_package": "debug",
    "log_http": "debug",
    "log_auth": "debug",
    "log": "debug",
    "export_file": "",
    "export_path": format(CWD_PATH),
    "export_format": "json",
    "export_overwrite": False,
}

REQUIRED = ["url", "key", "secret"]

LOG_CHOICES = ["debug", "info", "warning", "error", "critical"]


def connect_options(func):
    """Combine commonly appearing @click.option decorators."""
    #
    @click.option(
        "--url",
        default=DEFAULTS["url"],
        help="URL of Axonius instance.",
        metavar="URL",
        prompt="URL of Axonius instance",
        show_envvar=True,
    )
    @click.option(
        "--key",
        default=DEFAULTS["key"],
        help="API Key of user in Axonius instance.",
        metavar="KEY",
        prompt="API Key of user in Axonius instance",
        hide_input=True,
        show_envvar=True,
    )
    @click.option(
        "--secret",
        default=DEFAULTS["secret"],
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


def root_options(func):
    """Combine commonly appearing @click.option decorators."""
    #
    @click.option(
        "--proxy",
        default=DEFAULTS["proxy"],
        help="Proxy to use to connect to Axonius instance.",
        metavar="PROXY",
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--certpath",
        default=DEFAULTS["certpath"],
        type=click.Path(exists=True, resolve_path=True),
        help="Path to SSL certificate.",
        metavar="PATH",
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--certverify/--no-certverify",
        default=DEFAULTS["certverify"],
        help="Perform SSL Certificate Verification.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--certwarn/--no-certwarn",
        default=DEFAULTS["certwarn"],
        help="Show warning for self-signed SSL certificates.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--wraperror/--no-wraperror",
        default=DEFAULTS["wraperror"],
        help="Show an error string instead of the full exception.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--verbose/--no-verbose",
        default=DEFAULTS["verbose"],
        help="Show more information.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--log-package",
        default=DEFAULTS["log_package"],
        help="Logging level to use for package logger.",
        type=click.Choice(LOG_CHOICES),
        show_envvar=True,
        show_default=True,
    )
    @click.version_option(version.__version__)
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
        default=DEFAULTS["export_file"],
        help="Export to a file in export-path instead of printing to STDOUT.",
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-path",
        default=DEFAULTS["export_path"],
        help="Path to create export_file in.",
        type=click.Path(exists=False, resolve_path=True),
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-format",
        default=DEFAULTS["export_format"],
        help="Format to use for STDOUT or export-file.",
        type=click.Choice(["csv", "json"]),
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-overwrite/--no-export-overwrite",
        default=DEFAULTS["export_overwrite"],
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

    def __init__(self, **kwargs):
        """Pass."""
        print(locals())
        self.kwargs = kwargs
        self.obj = None
        for k, v in DEFAULTS.items():
            setattr(self, k, v)

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

    def export(self, data):
        """Pass."""
        ex_file = self.export_file
        ex_path = self.export_path
        ex_overwrite = self.export_overwrite

        if not ex_file:
            click.echo(data)
            return

        path = tools.resolve_path(ex_path)
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        full_path = path / ex_file
        mode = "created"
        if full_path.exists():
            if not ex_overwrite:
                msg = "Export file {p} already exists and export-overwite is False!"
                msg = msg.format(p=full_path)
                self.echo_error(msg=msg)
            mode = "overwritten"

        full_path.touch(mode=0o600)
        full_path.write_text(data)

        msg = "Export file {p!r} {mode}!"
        msg = msg.format(p=format(full_path), mode=mode)
        self.echo_ok(msg)

    def echo_ok(self, msg):
        """Pass."""
        if self.verbose:
            ok(msg)

    def echo_error(self, msg):
        """Pass."""
        error(msg)

    def echo_warn(self, msg):
        """Pass."""
        warn(msg)

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
        with warnings.catch_warnings(record=True) as caught_warnings:
            try:
                self.obj.start()
            except Exception as exc:
                if self.wraperror:
                    self.echo_error(format(exc))
                raise
            for caught_warning in caught_warnings:
                msg = format(caught_warning.message)
                if isinstance(caught_warning.message, SSLWARN_CLS):
                    warn(SSLWARN_MSG)
                    continue
                warn(msg)
        # warnings suck.
        warnings.simplefilter("ignore", SSLWARN_CLS)

    def start_client(self):
        """Pass."""
        if not getattr(self, "obj", None):
            try:
                self.obj = connect.Connect(
                    url=self.url,
                    key=self.key,
                    secret=self.secret,
                    proxy=self.proxy,
                    certpath=self.certpath,
                    certverify=self.certverify,
                    certwarn=self.certwarn,
                    wraperror=self.wraperror,
                )
            except Exception as exc:
                if self.wraperror:
                    self.echo_error(format(exc))
                raise

            self._start_client()
            self.echo_ok(msg=self.obj)
        return self.obj


pass_context = click.make_pass_decorator(Context, ensure=True)
