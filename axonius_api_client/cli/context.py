# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import warnings

import click
import requests

from ..connect import Connect
from ..tools import echo_error, echo_ok, echo_warn, json_load

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


class Context:
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

    # def read_stream_rows(self, stream, this_cmd):
    #     """Pass."""
    #     stream_name = format(getattr(stream, "name", stream))

    #     if stream.isatty():
    #         # its STDIN with no input
    #         msg = "No input provided on {s!r} for {tc!r}"
    #         msg = msg.format(s=stream_name, tc=this_cmd)
    #         echo_error(msg=msg, abort=True)

    #     # its STDIN with input or a file
    #     content = stream.read()

    #     msg = "Read {n} bytes from {s!r} for {tc!r}"
    #     msg = msg.format(n=len(content), s=stream_name, tc=this_cmd)
    #     echo_ok(msg=msg)

    #     content = content.strip()

    #     if not content:
    #         msg = "Empty content supplied in {s!r} for {tc!r}"
    #         msg = msg.format(s=stream_name, tc=this_cmd)
    #         echo_error(msg=msg, abort=True)

    #     with self.exc_wrap(wraperror=self.wraperror):
    #         rows = json_load(obj=content)

    #     msg = "Loaded JSON as {t} with length of {n} for {tc!r}"
    #     msg = msg.format(t=type(rows).__name__, tc=this_cmd, n=len(rows))
    #     echo_ok(msg=msg)

    #     return listify(obj=rows, dictkeys=False)

    # def export(self, data, export_file=None, export_path=None, export_overwrite=False):
    #     """Pass."""
    #     if not export_file:
    #         click.echo(data)
    #         return

    #     export_path = export_path or os.getcwd()

    #     path = get_path(obj=export_path)
    #     path.mkdir(mode=0o700, parents=True, exist_ok=True)

    #     full_path = path / export_file

    #     mode = "overwritten" if full_path.exists() else "created"

    #     if full_path.exists() and not export_overwrite:
    #         msg = "Export file {p} already exists and export-overwite is False!"
    #         msg = msg.format(p=full_path)
    #         self.echo_error(msg=msg)

    #     full_path.touch(mode=0o600)

    #     data = data.encode("utf-8")

    #     with full_path.open(mode="wb") as fh:
    #         fh.write(data)

    #     msg = "Exported file {p!r} {mode}!"
    #     msg = msg.format(p=format(full_path), mode=mode)
    #     self.echo_ok(msg)

    @staticmethod
    def echo_ok(msg, **kwargs):
        """Pass."""
        echo_ok(msg=msg, **kwargs)

    @staticmethod
    def echo_error(msg, abort=True, **kwargs):
        """Pass."""
        echo_error(msg=msg, abort=abort, **kwargs)

    @staticmethod
    def echo_warn(msg, **kwargs):
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
                self.echo_ok(msg="Connected to {!r}".format(self.client._http.url))

        return self.client

    def read_stream(self, stream):
        """Pass."""
        stream_name = format(getattr(stream, "name", stream))

        if stream.isatty():
            self.echo_error(msg=f"No input provided on {stream_name!r}", abort=True)

        # its STDIN with input or a file
        content = stream.read().strip()
        self.echo_ok(msg=f"Read {len(content)} bytes from {stream_name!r}")

        if not content:
            self.echo_error(msg=f"Empty content supplied to {stream_name!r}", abort=True)

        return content

    def read_stream_json(self, stream, expect):
        """Pass."""
        content = self.read_stream(stream=stream)

        try:
            content = json_load(obj=content, error=True)
        except Exception as exc:
            self.echo_error(msg=f"Invalid JSON supplied: {exc}", abort=True)

        if not isinstance(content, expect):

            self.echo_error(
                msg=f"JSON supplied is {type(content)}, required type is {expect}",
                abort=True,
            )

        return content


pass_context = click.make_pass_decorator(Context, ensure=True)
