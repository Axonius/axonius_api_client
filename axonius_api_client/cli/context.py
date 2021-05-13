# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import warnings

import click
import requests

from ..connect import Connect
from ..tools import bom_strip, echo_error, echo_ok, echo_warn, json_load, read_stream

CONTEXT_SETTINGS = {"auto_envvar_prefix": "AX"}
SSLWARN_CLS = requests.urllib3.exceptions.InsecureRequestWarning
SSLWARN_MSG = """Unverified HTTPS request!

To enable certificate validation:
  * Set the variable: AX_CERTPATH=/path/to/cert_or_ca_bundle
  * Supply the option: -cp/--cert-path /path/to/cert_or_ca_bundle

To silence this message:
  * Set the variable: AX_CERTWARN=n
  * Supply the option: -ncw/--no-cert-warn
"""


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


class AliasedGroup(click.Group):
    """Pass."""

    def get_command(self, ctx, cmd_name):
        """Pass."""
        rv = click.Group.get_command(self, ctx, cmd_name)

        if rv is not None:
            return rv

        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]

        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])

        msg = "Too many matches for {v!r}: {matches}"
        msg = msg.format(v=cmd_name, matches=", ".join(sorted(matches)))
        ctx.fail(msg)


class exc_wrapper:
    """Pass."""

    EXCLUDES = (SystemExit, click.exceptions.Exit)

    def __init__(self, wraperror=True, abort=True):
        """Pass."""
        self.wraperror = wraperror
        self.abort = abort

    def __enter__(self):
        """Pass."""
        return self

    def __exit__(self, exc, value, traceback):
        """Pass."""
        if value and self.wraperror and not isinstance(value, self.EXCLUDES):
            cls = value.__class__
            msg = f"WRAPPED EXCEPTION: {cls.__module__}.{cls.__name__}\n{value}"
            echo_error(msg=msg, abort=self.abort)


class Context:
    """Pass."""

    exc_wrap = exc_wrapper
    QUIET = False

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

    def echo_ok(self, msg, **kwargs):
        """Pass."""
        if not getattr(self, "QUIET", False):
            echo_ok(msg=msg, **kwargs)

    def echo_error(self, msg, abort=True, **kwargs):
        """Pass."""
        echo_error(msg=msg, abort=abort, **kwargs)

    def echo_warn(self, msg, **kwargs):
        """Pass."""
        echo_warn(msg=msg, **kwargs)

    @property
    def wraperror(self):
        """Pass."""
        return self._connect_args.get("wraperror", True)

    def start_client(self, url, key, secret, echo=True, **kwargs):
        """Pass."""
        if not getattr(self, "client", None):
            connect_args = {}
            connect_args.update(self._connect_args)
            connect_args.update(kwargs)
            connect_args["url"] = url
            connect_args["key"] = key
            connect_args["secret"] = secret

            with self.exc_wrap(wraperror=self.wraperror):
                self.client = Connect(**connect_args)

                with warnings.catch_warnings(record=True) as caught_warnings:
                    self.client.start()

                for caught_warning in caught_warnings:
                    wmsg = caught_warning.message
                    is_ssl = isinstance(wmsg, SSLWARN_CLS)
                    wmsg = SSLWARN_MSG if is_ssl else wmsg
                    wmsg = format(wmsg)
                    self.echo_warn(wmsg)

            # warnings suck.
            warnings.simplefilter("ignore", SSLWARN_CLS)

            if echo:
                self.echo_ok(msg=str(self.client))

            self.days_echo(
                msg="Trial expires in {days} days!!!", days=self.client.instances.trial_days_left
            )
            self.days_echo(
                msg="License expires in {days} days!!!",
                days=self.client.instances.license_days_left,
            )

        return self.client

    def days_echo(self, msg, days, info=45, warn=30, error=15):
        """Pass."""
        if not isinstance(days, int):
            return

        if days <= error:
            self.echo_error(msg.format(days=days), abort=False)
            return

        if days <= warn:
            self.echo_warn(msg.format(days=days))
            return

        if days <= info:
            self.echo_ok(msg.format(days=days))
            return

    def read_stream(self, stream, strip_bom=True):
        """Pass."""
        try:
            content = read_stream(stream=stream)
        except Exception as exc:
            self.echo_error(msg=f"Unable to read from input stream: {exc}", abort=True)
        if strip_bom:
            content = bom_strip(content=content)
        return content

    def read_stream_json(self, stream, expect=None):
        """Pass."""
        content = self.read_stream(stream=stream)

        try:
            content = json_load(obj=content, error=True)
        except Exception as exc:
            self.echo_error(msg=f"Invalid JSON supplied: {exc}", abort=True)

        if expect is not None and not isinstance(content, expect):

            self.echo_error(
                msg=f"JSON supplied is {type(content)}, required type is {expect}",
                abort=True,
            )

        return content


pass_context = click.make_pass_decorator(Context, ensure=True)
