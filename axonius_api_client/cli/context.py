# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import warnings

import click

from .. import connect, tools
from . import cli_constants


class exc_wrapper(object):
    """Pass."""

    EXCLUDES = (SystemExit, click.exceptions.Exit)

    def __init__(self, wraperror=True):
        """Pass."""
        self.wraperror = wraperror

    def __enter__(self):
        """Pass."""
        return self

    def __exit__(self, exc, value, traceback):
        """Pass."""
        if value and self.wraperror and not isinstance(value, self.EXCLUDES):
            msg = "WRAPPED EXCEPTION: {c.__module__}.{c.__name__}\n{v}"
            msg = msg.format(c=value.__class__, v=value)
            Context.echo_error(msg)


class Context(object):
    """Pass."""

    exc_wrap = exc_wrapper

    def __init__(self):
        """Pass."""
        self.client = None
        self._connect_args = {}

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return format(self.client)

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

        data = data.encode("utf-8")

        with full_path.open(mode="wb") as fh:
            fh.write(data)

        msg = "Exported file {p!r} {mode}!"
        msg = msg.format(p=format(full_path), mode=mode)
        self.echo_ok(msg)

    @staticmethod
    def echo_ok(msg, **kwargs):
        """Pass."""
        click.secho(cli_constants.OK_TMPL.format(msg=msg), **cli_constants.OK_ARGS)

    @staticmethod
    def echo_error(msg, abort=True, **kwargs):
        """Pass."""
        click.secho(cli_constants.ERROR_TMPL.format(msg=msg), **cli_constants.ERROR_ARGS)
        if abort:
            sys.exit(1)

    @staticmethod
    def echo_warn(msg, **kwargs):
        """Pass."""
        click.secho(cli_constants.WARN_TMPL.format(msg=msg), **cli_constants.WARN_ARGS)

    @property
    def wraperror(self):
        """Pass."""
        return self._connect_args.get("wraperror", True)

    def start_client(self, url, key, secret, **kwargs):
        """Pass."""
        if not getattr(self, "client", None):
            connect_args = {}
            connect_args.update(self._connect_args)
            connect_args.update(kwargs)
            connect_args["url"] = url
            connect_args["key"] = key
            connect_args["secret"] = secret

            with self.exc_wrap(wraperror=self.wraperror):
                self.client = connect.Connect(**connect_args)

                with warnings.catch_warnings(record=True) as caught_warnings:
                    self.client.start()

                for caught_warning in caught_warnings:
                    wmsg = caught_warning.message
                    is_ssl = isinstance(wmsg, cli_constants.SSLWARN_CLS)
                    wmsg = cli_constants.SSLWARN_MSG if is_ssl else wmsg
                    wmsg = format(wmsg)
                    self.echo_warn(wmsg)

            # warnings suck.
            warnings.simplefilter("ignore", cli_constants.SSLWARN_CLS)

            self.echo_ok(msg=self.client)

        return self.client

    def handle_export(
        self,
        raw_data,
        formatters,
        export_format,
        export_file,
        export_path,
        export_overwrite,
        ctx=None,
        reason=cli_constants.REASON,
        # fmt: off
        **kwargs
        # fmt: on
    ):
        """Pass."""
        if export_format not in formatters:
            self.echo_error(msg=reason.format(ef=export_format, sf=list(formatters)))

        with self.exc_wrap(wraperror=self.wraperror):
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
