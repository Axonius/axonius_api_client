# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import importlib
import pathlib
import typing as t
import warnings

import click
import urllib3.exceptions

from ..connect import Connect
from ..constants.ctypes import PathLike
from ..tools import (
    bom_strip,
    echo_debug,
    echo_error,
    echo_ok,
    echo_warn,
    extract_kvs_auto,
    is_str,
    json_load,
    listify,
    read_stream,
)

CONTEXT_SETTINGS: dict = {"auto_envvar_prefix": "AX"}
SSL_WARN_CLS: t.Type[Warning] = urllib3.exceptions.InsecureRequestWarning
SSL_WARN_MSG: str = """Unverified HTTPS request!

To enable certificate validation:
  * axonshell: Set the variable: AX_CERTPATH="/path/to/cert_or_ca_bundle"
    or supply the option: -cp/--cert-path "/path/to/cert_or_ca_bundle"
  * library: Connect(url=..., certpath="/path/to/cert_or_ca_bundle")

To silence this message:
  * axonshell: Set the variable: AX_CERTWARN="n" or supply the option: -ncw/--no-cert-warn
  * library: Connect(url=..., certwarn=False)
"""


def load_cmds(path: PathLike, package: str, group: click.Group):
    """Load the commands for a given path."""
    path = pathlib.Path(path)

    for item in path.parent.glob("cmd_*.py"):
        module = importlib.import_module(f".{item.stem}", package=package)
        module_cmd = getattr(module, "cmd", None)
        if callable(module_cmd):
            # noinspection PyTypeChecker
            group.add_command(module_cmd)


class DictParam(click.ParamType):
    """Pass."""

    name = "dict_param"

    def __init__(self, split_kv: str = "="):
        """Pass."""
        self.split_kv = split_kv

    def convert(self, value, param, ctx) -> t.Union[dict, t.Tuple[str, str]]:
        """Pass."""
        if isinstance(value, (str, bytes)):
            example = f"key1{self.split_kv}value1"
            example = f"\nExample: {example!r}"
            splitit = f"key/value split character {self.split_kv!r}"
            parts = value.split("=", 1)
            if len(parts) != 2:
                self.fail(f"Missing {splitit} in value {value!r}{example}", param, ctx)
            s_key, s_val = parts
            s_key = s_key.strip()
            if not s_key:
                self.fail(f"Missing key before {splitit} in value {value!r}{example}", param, ctx)
            return s_key, s_val
        return value


class DictOption(click.Option):
    """Custom dictionary type option for Click."""

    param_type_name = "dict_option"
    split_kv: str = "="
    constructor: t.Type[t.Mapping] = dict
    help_post: t.List[str] = None

    def __init__(self, *args, **kwargs):
        """Pass."""
        self.split_kv = kwargs.pop("split_kv", self.split_kv)
        self.help_post = listify(kwargs.pop("help_post", self.help_post_default))
        self.constructor = kwargs.pop("constructor", self.constructor)

        help_str = kwargs.get("help", "")
        kwargs["type"] = DictParam(split_kv=self.split_kv)
        kwargs["multiple"] = True
        kwargs["is_flag"] = False
        kwargs["help"] = "  ".join([x for x in [help_str, *self.help_post] if is_str(x)])
        kwargs.setdefault("show_envvar", True)
        kwargs.setdefault("show_default", False)
        super().__init__(*args, **kwargs)

    @property
    def help_post_default(self) -> t.List[str]:
        """Pass."""
        example = f"key1{self.split_kv}value1"
        example = f"Example: {example!r}"
        return [
            f"({example})",
            "(env var parsed as CSV unless starts with 'json:')",
            "(env var CSV delimiter uses ; instead of , if starts with 'semi:')",
            "(multiples)",
        ]

    def to_info_dict(self):
        """Pass."""
        info_dict = super().to_info_dict()
        info_dict["split_kv"] = self.split_kv
        info_dict["constructor"] = self.constructor
        return info_dict

    def type_cast_value(self, ctx, value: t.Any) -> t.Optional[t.Mapping]:
        """Pass."""
        if isinstance(value, self.constructor):
            return value

        if value is not None:
            typed = [self.type(param=self, ctx=ctx, value=x) for x in value]
            # noinspection PyArgumentList
            return self.constructor(typed)
        return value

    def get_envvar(self, ctx) -> t.Optional[str]:
        """Pass."""
        if (
            not self.envvar
            and self.allow_from_autoenv
            and ctx.auto_envvar_prefix is not None
            and self.name is not None
        ):
            return f"{ctx.auto_envvar_prefix}_{self.name.upper()}"
        return self.envvar

    def value_from_envvar(self, ctx) -> dict:
        """Pass."""
        value = self.resolve_envvar_value(ctx)
        if is_str(value):
            opts = ", ".join(self.opts) if isinstance(self.opts, (list, tuple)) else self.opts
            src = ["", f"OS Environment variable: {self.get_envvar(ctx)!r}", f"Option: {opts}"]
            value = extract_kvs_auto(value=value, split_kv=self.split_kv, src=src)
        return value


class SplitEquals(DictParam):
    """Pass."""

    name = "split_equals"


class AliasedGroup(click.Group):
    """Pass."""

    def get_command(self, ctx, cmd_name):
        """Pass."""
        rv = click.Group.get_command(self, ctx, cmd_name)

        if rv is not None:
            return rv

        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]

        if matches and len(matches) != 1:  # pragma: no cover
            ctx.fail(f"Too many matches for {cmd_name!r}: {matches}")

        return click.Group.get_command(self, ctx, matches[0]) if len(matches) == 1 else None


class exc_wrapper:
    """Pass."""

    EXCLUDES = (
        SystemExit,
        RuntimeError,
        click.exceptions.Exit,
        click.exceptions.Abort,
        click.exceptions.ClickException,
    )

    def __init__(self, wraperror=True, abort=True):
        """Pass."""
        self.wraperror = wraperror
        self.abort = abort

    def __enter__(self):
        """Pass."""
        return self

    def __exit__(self, exc, value, traceback):  # pragma: no cover
        """Pass."""
        if value and self.wraperror and not isinstance(value, self.EXCLUDES):
            self.exc = exc
            self.value = value
            self.traceback = traceback
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

    def __str__(self):  # pragma: no cover
        """Show object info.

        Returns:
            :obj:`str`

        """
        return format(self.client)

    def __repr__(self):  # pragma: no cover
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    def echo_ok(self, msg, **kwargs):
        """Pass."""
        if not self.QUIET:
            echo_ok(msg=msg, **kwargs)

    def echo_debug(self, msg, **kwargs):  # pragma: no cover
        """Pass."""
        if not self.QUIET:
            echo_debug(msg=msg, **kwargs)

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

    def create_client(
        self, url: str, key: t.Optional[str] = None, secret: t.Optional[str] = None, **kwargs
    ):
        """Pass."""
        connect_args = {}
        connect_args.update(self._connect_args)
        connect_args.update(kwargs)
        connect_args["url"] = url
        connect_args["key"] = key
        connect_args["secret"] = secret

        with self.exc_wrap(wraperror=self.wraperror):
            self.client = Connect(**connect_args)

        return self.client

    def start_client(self, url, key, secret, echo=True, **kwargs):
        """Pass."""
        if not getattr(self, "client", None):
            self.create_client(url=url, key=key, secret=secret, **kwargs)

            with self.exc_wrap(wraperror=self.wraperror):
                with warnings.catch_warnings(record=True) as caught_warnings:
                    self.client.start()

                for caught_warning in caught_warnings:  # pragma: no cover
                    warn_msg = caught_warning.message
                    is_ssl = isinstance(warn_msg, SSL_WARN_CLS)
                    warn_msg = SSL_WARN_MSG if is_ssl else warn_msg
                    warn_msg = format(warn_msg)
                    self.echo_warn(warn_msg)

            # warnings suck.
            warnings.simplefilter("ignore", SSL_WARN_CLS)

            if echo:
                self.echo_ok(msg=str(self.client))

            self.days_echo(
                msg="Trial expires in {days} days",
                days=self.client.instances.trial_days_left,
                days_info=45,
                days_warn=30,
                days_error=15,
            )
            self.days_echo(
                msg="License expires in {days} days",
                days=self.client.instances.license_days_left,
                days_info=90,
                days_warn=60,
                days_error=30,
            )
            self.days_echo(
                msg="SSL Certificate expires in {days} days",
                days=self.client.ssl_days_left,
                days_info=120,
                days_warn=90,
                days_error=60,
            )
        return self.client

    def days_echo(
        self,
        msg: str,
        days: t.Optional[t.Union[int, float]] = None,
        days_info: t.Optional[t.Union[int, float]] = 45,
        days_warn: t.Optional[t.Union[int, float]] = 30,
        days_error: t.Optional[t.Union[int, float]] = 15,
    ):
        """Echo a message to console in various colors depending on the days.

        Args:
            msg: The message to echo.
            days: The number of days.
            days_info: The number of days to use for info color.
            days_warn: The number of days to use for warn color.
            days_error: The number of days to use for error color.
        """
        try:
            msg = msg.format(**locals())
        except KeyError:
            pass

        bits = [
            f"error<={days_error}",
            f"warn<={days_warn}",
            f"info<={days_info}",
            f"debug=None or > info",
        ]
        bits = ", ".join(bits)
        msg = f"{msg} ({bits})"
        method = self.echo_debug

        if isinstance(days, (int, float)):
            if isinstance(days_error, (int, float)) and days <= days_error:
                method = self.echo_error
            elif isinstance(days_warn, (int, float)) and days <= days_warn:
                method = self.echo_warn
            elif isinstance(days_info, (int, float)) and days <= days_info:
                method = self.echo_ok

        method(msg=msg, abort=False)

    def read_stream(self, stream, strip_bom: bool = True) -> t.Optional[str]:
        """Pass."""
        try:
            content = read_stream(stream=stream)
        except Exception as exc:
            self.echo_error(msg=f"Unable to read from input stream: {exc}", abort=True)
        else:
            if strip_bom:
                content = bom_strip(content=content)
            return content

    def read_stream_json(
        self,
        stream,
        expect: t.Optional[type] = None,
        expect_items: t.Optional[type] = None,
        items_min: t.Optional[int] = None,
    ):
        """Pass."""
        content = self.read_stream(stream=stream)

        try:
            content = json_load(obj=content, error=True)
        except Exception as exc:  # pragma: no cover
            self.echo_error(msg=f"Invalid JSON supplied: {exc}", abort=True)

        if expect is not None and not isinstance(content, expect):
            self.echo_error(
                msg=f"JSON supplied is {type(content)}, required type is {expect}",
                abort=True,
            )

        if expect_items is not None:  # pragma: no cover
            errs = []
            for idx, item in enumerate(content):
                if not isinstance(item, expect_items):
                    errs.append(f"Item #{idx + 1}/{len(content)} is type {type(item)}")

            if errs:
                errs = "\n  " + "\n  ".join(errs)
                self.echo_error(
                    msg=f"List items do not match required type {expect_items}:{errs}",
                    abort=True,
                )

        if isinstance(items_min, int) and not len(content) >= items_min:
            self.echo_error(
                msg=(
                    f"Must supply at least {items_min} items, but only {len(content)} "
                    "items supplied"
                ),
                abort=True,
            )
        return content


pass_context = click.make_pass_decorator(Context, ensure=True)
