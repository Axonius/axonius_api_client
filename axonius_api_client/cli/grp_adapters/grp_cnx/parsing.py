# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import abc
import json
import os
import re
import tempfile
from typing import Any, Dict, List, Optional, Pattern, Tuple, Type, Union

from ....constants.adapters import CNX_SANE_DEFAULTS
from ....tools import (
    coerce_bool,
    coerce_int,
    echo_debug,
    echo_error,
    echo_ok,
    echo_warn,
    get_subcls,
    is_email,
    is_str,
    join_kv,
    pathlib,
    strip_left,
)
from ...context import click

"""TODOS

- re-ensure tools.py coverage (def need is_str, is_email)
- max/min int
- unchanged

- figure out update methods
- via post-mortem check, handle dependencies like:
{
      "dependency": "enable_client_side_cert",
      "name": "client_side_cert",
      "title": "Client Certificate File (.pem)",
      "type": "file",
      "required": false,
      "hide_value": false
}


"""


class Defaults:
    """Pass."""

    use_sane_defaults: bool = True
    prompt_for_optional: bool = True
    prompt_for_default: bool = True
    prompt_for_missing_required: bool = True
    error_as_exc: bool = False
    ignore_unknowns: bool = False
    show_schemas: bool = False
    show_defaults: bool = False
    prompt_for_previous: bool = False


class SchemaError(ValueError):
    """Error in schema."""

    pass


class PromptError(ValueError):
    """Error during prompting."""

    pass


class SchemaClick(click.types.ParamType):
    """Custom param type to prompt for schema values."""

    def __init__(self, schema: "Schema") -> None:
        """Override."""
        self.name = f"{schema}"
        self.schema = schema

    def to_info_dict(self) -> Dict[str, Any]:
        """Override."""
        info_dict = super().to_info_dict()
        info_dict["schema"] = self.schema
        return info_dict

    def convert(
        self,
        value: Any,
        param: Optional[click.Parameter] = None,
        ctx: Optional[click.Context] = None,
    ) -> Any:
        """Override."""
        try:
            return self.schema.parse_value(value)
        except Exception as exc:
            self.fail(message=click.style(text=f"{exc}", fg="red"), param=param, ctx=ctx)


class Schema(abc.ABC):
    """Schema container abstract base class."""

    NULL: List[str] = ["None"]
    NULL_PARSED: Any = None
    USE_DEFAULT: str = "USE_DEFAULT"
    UNCHANGED_RE: Pattern = re.compile(r"\[.*unchanged.*\]", re.I | re.DOTALL)
    UNCHANGED_STRS: List[str] = ['["unchanged"]', "['unchanged']"]
    UNCHANGED_ARR: List[str] = ["unchanged"]
    HIDDEN_KEYS: List[str] = ["secret", "key", "password"]

    SRC_NONE: str = "no schema default, or sane default, or previous config value"
    SRC_SCHEMA: str = "schema default"
    SRC_PREVIOUS: str = "previous config value"
    SRC_SANE: str = "sane default"

    def __init__(
        self,
        schema: dict,
        adapter_name: str,
        use_sane_defaults: bool = Defaults.use_sane_defaults,
        prompt_for_optional: bool = Defaults.prompt_for_optional,
        prompt_for_default: bool = Defaults.prompt_for_default,
        prompt_for_missing_required: bool = Defaults.prompt_for_missing_required,
        prompt_for_previous: bool = Defaults.prompt_for_previous,
        error_as_exc: bool = Defaults.error_as_exc,
    ):
        """Container for adapter connection schemas."""
        if schema["type"] != self.for_type():
            raise SchemaError(f"Schema type mismatch {self.for_type()} != {schema['type']}")

        self.schema: dict = schema
        self.adapter_name: str = adapter_name
        self.use_sane_defaults: bool = use_sane_defaults
        self.prompt_for_optional: bool = prompt_for_optional
        self.prompt_for_default: bool = prompt_for_default
        self.prompt_for_missing_required: bool = prompt_for_missing_required
        self.prompt_for_previous: bool = prompt_for_previous
        self.error_as_exc: bool = error_as_exc
        self.in_prompt_mode: bool = False
        self.has_previous_value: bool = False
        self.previous_value: Any = None

    @staticmethod
    @abc.abstractmethod
    def for_type() -> str:
        """Get the 'type' key value that should map for this Schema object."""
        raise NotImplementedError()

    @abc.abstractmethod
    def parse_value(self, value: Any) -> Any:
        """Parse the supplied value."""
        raise NotImplementedError()

    @property
    def _parse_attrs(self) -> List[str]:
        """Attrs to include in parse_attrs output."""
        return [
            "required",
            "prompt_for_missing_required",
            "prompt_for_optional",
            "prompt_for_default",
            "default_value",
            "default_source",
        ]

    @property
    def parse_attrs(self) -> List[str]:
        """Get attrs to print as part of parsing."""
        return self._ainfos(self._parse_attrs)

    def parse(
        self,
        config: dict,
        config_previous: Optional[dict] = None,
    ) -> Any:
        """Parse value for this schema from config or config_previous."""

        def join(value):
            return ", ".join(value)

        self.has_previous_value = False
        config_previous = config_previous or {}

        if self.name in config:
            self.debug("Found value in supplied config, validating")
            value = config[self.name]
            if self.is_use_default(value=value):
                value = self.resolve_use_default(value=value)
            parsed = self.parse_value(value)
            return parsed

        if self.name in config_previous:
            value = config_previous[self.name]
            self.has_previous_value = True
            self.previous_value = value
            reasons = [
                "Did not find value in supplied config",
                "found value in previous config",
                self._ainfo("prompt_for_previous"),
            ]
            if self.prompt_for_previous:
                return self.prompt(reason=join(reasons))

            self.resolved(parsed=value, reason=join(reasons))
            return value

        src = "supplied config or previous config" if config_previous else "supplied config"
        reasons = [f"value not provided in {src}", *self.parse_attrs]

        if not self.prompt_for_default and self.default_exists:
            self.resolved(parsed=self.default_value, reason=join(reasons))
            return self.default_value

        if self.required:
            if not self.prompt_for_missing_required:
                reasons = "Reasons:\n  - " + "\n  - ".join(reasons)
                self.error(f"Must supply value! {reasons}")
            return self.prompt(reason=join(reasons))

        if not self.prompt_for_optional:
            self.resolved(parsed=self.default_value, reason=join(reasons))
            return self.default_value

        parsed = self.prompt(reason=join(reasons))
        return parsed

    @property
    def prompt_text_pre(self) -> List[str]:
        """Text to show before prompt."""
        ret = []
        if self.hide_value:
            ret.append("Input will be hidden!")

        if not self.required and self.NULL:
            ret.append(f"Use {self.nulls_str} for {self.NULL_PARSED}.")

        if self.enum:
            ret.append(f"Value must be one of: {self.enum}")

        if self.prompt_default is not None:
            vinfo = self.vinfo(value=self.prompt_default, hide=False)
            ret.append(f"Press enter to accept default value of {vinfo}")

        return ret

    @property
    def prompt_text(self) -> str:
        """Text to show when prompting."""
        ret = "Enter value"
        pre = self.prompt_text_pre
        pre_str = click.style(text="\n".join(pre) + "\n", fg="cyan") if pre else ""
        return f"{pre_str}{ret}"

    @property
    def prompt_default(self) -> Any:
        """Prompt default to use."""

        def default_or_null(value):
            return self.NULL[0] if value is None and self.NULL else value

        if self.default_exists:
            return default_or_null(self.default_value)

        if not self.required and self.NULL:
            return default_or_null(self.default_value)

        return None

    @property
    def prompt_args(self) -> dict:
        """Arguments to use when calling :meth:`click.prompt`."""
        ret = {
            "text": self.prompt_text,
            "type": self.click_type,
            "err": True,
            "hide_input": self.hide_value,
            "show_default": False,
            "default": self.prompt_default,
        }
        return ret

    def prompt(self, reason: str = "", **kwargs):
        """Prompt the user and return the parsed value."""
        self.in_prompt_mode = True
        prompt_args = {}
        prompt_args.update(self.prompt_args)
        prompt_args.update(kwargs)

        if reason:
            self.debug(f"Prompting due to: {reason}")

        echo_ok(msg=f"{self!r}", bold=False)
        parsed = click.prompt(**prompt_args)
        self.in_prompt_mode = False
        return parsed

    def parse_pre(self, value: Any) -> Tuple[bool, Any]:
        """Parse value for NULL_PARSED or UNCHANGED_ARR."""
        if value in self.NULL or value == self.NULL_PARSED:
            if self.required:
                self.error(f"Value is required, can not use empty sentinel {value!r}")

            parsed = self.NULL_PARSED
            self.resolved(value=value, parsed=parsed, reason="NULL sentinel")
            return True, parsed

        if self.is_unchanged(value=value):
            parsed = self.UNCHANGED_ARR
            self.resolved(value=value, parsed=parsed, reason="UNCHANGED sentinel")
            return True, parsed

        return False, value

    @property
    def click_type(self) -> Optional[click.types.ParamType]:
        """Parameter type to use when prompting."""
        return SchemaClick(schema=self)

    @classmethod
    def load_type(cls, schema: dict, **kwargs) -> "Schema":
        """Load a schema into the corresponding Schema object."""
        return cls.get_types()[schema["type"]](schema=schema, **kwargs)

    @classmethod
    def load_types(cls, schemas: List[dict], **kwargs) -> List["Schema"]:
        """Load a list of schemas into their corresponding Schema objects."""
        return [cls.load_type(schema=x, **kwargs) for x in schemas]

    @classmethod
    def get_types(cls) -> Dict[str, Type]:
        """Get all subclasses mapped by type key."""
        return {x.for_type(): x for x in get_subcls(cls)}

    def __str__(self) -> str:
        """Builtin."""
        return f"Schema {self.name!r}"

    def __repr__(self) -> str:
        """Builtin."""
        vals = [
            f"Schema {self.name!r} for adapter {self.adapter_name!r}:",
            *self.to_strs(),
        ]
        return "\n".join(vals)

    @property
    def str_properties(self) -> List[str]:
        """List of properties to print in repr."""
        return [
            "title",
            "name",
            "type",
            "required",
            "hide_value",
            "description" if self.description else "",
            "default_exists",
            "default_value",
            "default_source",
            "prompt_default" if self.prompt_default is not None else "",
            "enum" if self.enum else "",
        ]

    def to_strs(self) -> List[str]:
        """Get the properties for this Schema object in pretty printed format."""
        props = [x for x in self.str_properties if x and hasattr(self, x)]
        values = [getattr(self, x) for x in props]
        values = [x if "\n" in str(x) else repr(x) for x in values]
        docs = [getattr(self.__class__, x).__doc__ for x in props]
        tmpl = "  # {doc}\n  {prop}: {value}\n".format
        items = [tmpl(prop=x[0], value=x[1], doc=x[2]) for x in zip(props, values, docs)]
        return items

    def debug(self, msg: str) -> str:
        """Echo a debug message to console."""
        msg = f"{self}: {msg}"
        echo_debug(msg=msg)
        return msg

    def vinfo(self, value, hide: bool = True) -> str:
        """Get the info for a value, hiding the value as necessary."""
        show = self.hide(value) if hide else value
        return f"{show!r} (type {type(value).__name__})"

    def _ainfo(self, attr: str) -> str:
        """Pass."""
        return f"{attr}={getattr(self, attr, None)}"

    def _ainfos(self, attrs: List[str]) -> List[str]:
        """Pass."""
        return [self._ainfo(x) for x in attrs]

    def resolved(self, parsed: Any, value: Any = None, reason: str = "") -> str:
        """Echo a debug resolved message to console."""
        msg = f"Resolved value to {self.vinfo(parsed)}"
        msg += f" from value {self.vinfo(value)}" if value is not None and value != parsed else ""
        post = f" reason: {reason}" if reason else ""
        msg = f"{self}: {msg}{post}"
        echo_debug(msg=msg, bold=True)
        return msg

    def info(self, msg: str) -> str:
        """Echo an info message to console."""
        msg = f"{self}: {msg}"
        echo_ok(msg=msg)
        return msg

    def warn(self, msg: str) -> str:
        """Echo a warning message to console."""
        msg = f"{self}: {msg}"
        echo_warn(msg=msg)
        return msg

    def error(self, msg: str, abort: bool = True) -> str:
        """Echo an error message to console and abort."""
        if self.in_prompt_mode and abort:
            raise PromptError(f"While in prompt mode for {self}: {msg}")

        msg = f"Error in {self}: {msg}\n\n{self!r}"

        if self.error_as_exc and abort:
            raise SchemaError(msg)

        echo_error(msg=msg, abort=abort)
        return msg

    @property
    def title(self) -> str:
        """Title in GUI for this config item."""
        return self.schema["title"]

    @property
    def description(self) -> Optional[str]:
        """Get description from schema for this config item."""
        return self.schema.get("description")

    @property
    def name(self) -> str:
        """Key used for setting this config item."""
        return self.schema["name"]

    @property
    def type(self) -> str:
        """Type of value that should be supplied."""
        return self.schema["type"]

    @property
    def enum(self) -> List[Union[str, int]]:
        """List of values that are allowed."""
        return self.schema.get("enum", [])

    @property
    def hide_value(self) -> bool:
        """Value will be hidden when printing/prompting."""
        return self.format_is_password or self.name in self.HIDDEN_KEYS

    @property
    def required(self) -> bool:
        """Value must be supplied."""
        return self.schema.get("required", False)

    @property
    def default(self) -> Optional[Any]:
        """REST API default value."""
        return self.schema.get("default")

    @property
    def default_exists(self) -> bool:
        """If this schema has a default or sane default."""
        return bool(self.has_previous_value or self.has_default or self.has_sane_default)

    @property
    def default_value(self) -> Any:  # noqa: D401
        """The default value to use when prompting/parsing."""
        if self.has_previous_value:
            return self.previous_value

        if self.has_default:
            return self.default

        if self.has_sane_default:
            return self.sane_default

        return None

    @property
    def default_source(self) -> str:
        """Where the default value came from."""
        if self.has_previous_value:
            return self.SRC_PREVIOUS

        if self.has_default:
            return self.SRC_SCHEMA

        if self.has_sane_default:
            return self.SRC_SANE

        return self.SRC_NONE

    @property
    def has_default(self) -> bool:
        """Check if this schema has a 'default' key."""
        return "default" in self.schema

    @property
    def has_sane_default(self) -> bool:
        """Check if sane defaults has an entry for this schema."""
        return self.use_sane_defaults and self.name in self.sane_defaults

    @property
    def sane_default(self) -> Any:
        """Sane default as defined in API client."""
        return self.sane_defaults.get(self.name)

    @property
    def sane_defaults(self) -> Any:
        """Sane defaults for this adapter as defined in API client."""
        return get_defaults_sane(self.adapter_name)

    @property
    def nulls_str(self) -> str:
        """Get the str version of self.NULL."""
        return " or ".join([f"{x!r}" for x in self.NULL])

    def resolve_use_default(self, value: Any) -> Any:
        """Resolve the use of :attr:`USE_DEFAULT`."""
        if not self.default_exists:
            self.error(f"Schema has {self.default_source} - can not {self.USE_DEFAULT}")

        self.resolved(
            value=value,
            parsed=self.default_value,
            reason=f"{self.default_source} due to value == {self.USE_DEFAULT}",
        )
        return self.default_value

    def is_use_default(self, value: Any) -> Any:
        """Check if value is :attr:`USE_DEFAULT`."""
        return value == self.USE_DEFAULT

    @property
    def format(self) -> Optional[str]:
        """Get the format from the schema."""
        return self.schema.get("format")

    @property
    def format_is_password(self) -> bool:
        """See if :attr:`format` == 'password'."""
        return self.format == "password"

    def is_unchanged(self, value: Any) -> bool:
        """Check if a string is unchanged."""
        return self.format_is_password and (
            value == self.UNCHANGED_ARR
            or value in self.UNCHANGED_STRS
            or bool(self.UNCHANGED_RE.search(str(value)))
        )

    def hide(self, value: Any) -> Any:
        """Get a hidden version of str value if applicable."""
        if (
            self.hide_value
            and isinstance(value, str)
            and value not in self.NULL
            and not self.is_unchanged(value=value)
        ):
            return f"{len(value)}_CHARACTERS_HIDDEN"
        return value

    def check_enum(self, value: Any) -> Any:
        """Check if a supplied value is one of :attr:`enum`."""
        if self.enum:
            if value not in self.enum:
                self.error(f"Value must be one of {self.enum!r}, not {value!r}")
        return value


class SchemaFile(Schema):
    """Schema container for 'file' type."""

    CONTENT: str = "CONTENT:"
    FILE_CHECKS: List[str] = ["{", "filename", "uuid", "}"]
    FILE_EX: str = '{"filename": "example.ccc", "uuid": "61fbed457990b10d07579b98"}'
    FILE_KEYS: List[str] = ["uuid", "filename"]

    @staticmethod
    def for_type() -> str:
        """Get the 'type' key value that should map for this Schema object."""
        return "file"

    @property
    def prompt_text_pre(self) -> List[str]:
        """Text to show before prompt."""
        ret = super().prompt_text_pre
        ret += [
            f"Can start value with {self.CONTENT} to create a file (single line with embedded \\n)",
            f"Can provide a JSON dictionary of an uploaded file, example: {self.FILE_EX}",
        ]
        return ret

    def parse_content(self, value: str) -> str:
        """Parse out content after :attr:`CONTENT`."""
        content = strip_left(obj=value, fix=self.CONTENT)
        prefix = f"axonshell-adapter:{self.adapter_name}-schema:{self.name}"
        handle, tmppath = tempfile.mkstemp(suffix=".tmp", prefix=prefix, text=True)
        parsed = pathlib.Path(tmppath).expanduser().resolve()
        self.debug(f"Writing {len(content)} bytes to file {parsed}")
        with os.fdopen(handle, "w") as fh:
            fh.write(content)
        self.resolved(parsed=parsed, reason=f"writing content after {self.CONTENT!r} to a tempfile")
        return parsed

    def is_file_object(self, value: Any) -> bool:
        """Check if a value is file dict."""
        return all([x in str(value) for x in self.FILE_CHECKS])

    def check_file_object(self, value: dict) -> dict:
        """Check a dictionary of a file object."""
        info = f"File object {self.vinfo(value)!r} "
        if not isinstance(value, dict):
            self.error(f"{info} must be a dictionary")

        parsed = {}

        errs = []
        for k in self.FILE_KEYS:
            v = value.get(k)
            if not is_str(value=v):
                errs.append(
                    f"Required file object key {k!r} must be a non empty string not {self.vinfo(v)}"
                )
            parsed[k] = v

        if errs:
            errs = "\n" + "\n".join(errs)
            self.error(f"{info} had errors:{errs}")

        self.resolved(value=value, parsed=parsed, reason="validating file object")
        return parsed

    def parse_file_object(self, value: Union[str, dict]) -> dict:
        """Parse file dict."""
        parsed = value

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except Exception as exc:
                self.error(msg=f"Invalid JSON in file dictionary: {exc}")
            else:
                self.resolved(value=value, parsed=parsed, reason="JSON string")

        parsed = self.check_file_object(value=parsed)
        return parsed

    def parse_file_path(self, value: Union[str, pathlib.Path]) -> pathlib.Path:
        """Parse pathlib."""
        if isinstance(value, str):
            parsed = pathlib.Path(value).expanduser().resolve()
            self.resolved(value=value, parsed=parsed, reason="path supplied as string")
        elif not isinstance(value, pathlib.Path):
            self.error(f"Value must be a string or a {pathlib.Path}, not {self.vinfo(value)}")
        return parsed

    def parse_value(self, value: Any) -> Optional[pathlib.Path]:
        """Parse the supplied value into a path or uploaded file obj."""
        is_pre_parsed, parsed = self.parse_pre(value=value)

        if not is_pre_parsed:
            if isinstance(value, str) and value.strip().startswith(self.CONTENT):
                parsed = self.parse_content(value=value)
            elif isinstance(parsed, dict):
                parsed = self.check_file_object(value=parsed)
            elif self.is_file_object(value=value):
                parsed = self.parse_file_object(value=value)
            else:
                parsed = self.parse_file_path(value=value)

        if isinstance(parsed, pathlib.Path) and not parsed.is_file():
            self.error(msg=f"No file found at {parsed}")

        return parsed


class SchemaBool(Schema):
    """Schema container for 'bool' type."""

    NULL: List[str] = []
    SANE_DEFAULT: bool = False

    @staticmethod
    def for_type() -> str:
        """Get the 'type' key value that should map for this Schema object."""
        return "bool"

    def parse_value(self, value: Any) -> bool:
        """Parse the supplied value into a boolean."""
        is_pre_parsed, parsed = self.parse_pre(value=value)
        try:
            parsed = coerce_bool(obj=value)
            self.resolved(value=value, parsed=parsed, reason="coerce_bool")
        except Exception as exc:
            self.error(f"{exc}")
        return parsed

    @property
    def has_sane_default(self) -> bool:
        """Check if sane defaults has an entry for this schema."""
        if self.use_sane_defaults:
            return True
        return super().has_sane_default

    @property
    def sane_default(self) -> Any:
        """Sane default as defined in API client."""
        if super().has_sane_default:
            return super().sane_default

        if self.use_sane_defaults:
            return self.SANE_DEFAULT
        return None


class SchemaInteger(Schema):
    """Schema container for 'integer' type."""

    @staticmethod
    def for_type() -> str:
        """Get the 'type' key value that should map for this Schema object."""
        return "integer"

    def parse_value(self, value: Any) -> int:
        """Parse the supplied value into an integer."""
        is_pre_parsed, parsed = self.parse_pre(value=value)
        if not is_pre_parsed:
            try:
                parsed = coerce_int(
                    obj=value,
                    max_value=self.max_value,
                    min_value=self.min_value,
                    valid_values=self.enum,
                )
                self.resolved(value=value, parsed=parsed, reason="coerce_int")
            except Exception as exc:
                self.error(f"{exc}")
        return parsed

    @property
    def max_value(self) -> Optional[int]:
        """Get the max value from the schema."""
        return self.schema.get("max")

    @property
    def min_value(self) -> Optional[int]:
        """Get the min value from the schema."""
        return self.schema.get("min")


class SchemaNumber(SchemaInteger):
    """Schema container for 'number' type."""

    @staticmethod
    def for_type() -> str:
        """Get the 'type' key value that should map for this Schema object."""
        return "number"


class SchemaArray(Schema):
    """Schema container for 'array' type."""

    NULL: List[str] = ["[]", "None"]
    NULL_PARSED: Any = []
    SPLIT: str = ","

    @staticmethod
    def for_type() -> str:
        """Get the 'type' key value that should map for this Schema object."""
        return "array"

    def parse_value(self, value: Any) -> Any:
        """Parse the supplied value into a list of strings."""
        is_pre_parsed, parsed = self.parse_pre(value=value)
        if not is_pre_parsed:
            parsed = [x.strip() for x in value.strip().split(self.SPLIT) if x.strip()]
            self.resolved(value=value, parsed=parsed, reason="string split on {self.SPLIT!r}")
            if not parsed and self.required:
                self.error(f"Empty value {parsed!r} after splitting {value!r} on {self.SPLIT!r}")
            parsed = self.check_enum(value=parsed)
        return parsed

    @property
    def prompt_text_pre(self) -> List[str]:
        """Text to show before prompt."""
        ret = super().prompt_text_pre
        ret.append(f"Enter values seperated by {self.SPLIT!r}")
        return ret

    @property
    def enum(self) -> List[Union[str, int]]:
        """Values that are allowed."""
        return [x["name"] for x in self.items_enum] or super().enum

    @property
    def enum_details(self) -> str:
        """Details on values that are allowed."""
        ret = ""
        if self.items_enum:
            tmpl = "Value: {name!r}, Description: {title}, type: {type}".format
            items = [tmpl(type=self.items_type, **x) for x in self.items_enum]
            ret = "\n    " + "\n    ".join(items)
        return ret

    @property
    def items_enum(self) -> dict:
        """Get the enum key from the items key found on this type."""
        return self.items.get("enum", [])

    @property
    def items_type(self) -> dict:
        """Get the type key from the items key found on this type."""
        return self.items.get("type", [])

    @property
    def items(self) -> dict:
        """Get the items key found on this type."""
        return self.schema.get("items", {})

    @property
    def str_properties(self) -> List[str]:
        """List of properties to print in repr."""
        ret = super().str_properties
        ret.append("enum_details" if self.enum_details else "")
        return ret

    def check_enum(self, value: Any) -> Any:
        """Check if a supplied value is one of :attr:`enum`."""
        if self.enum:
            unknowns = [x for x in value if x not in self.enum]
            if unknowns:
                self.error(
                    f"Invalid values supplied {unknowns!r}, values must be one of: {self.enum}"
                )
        return value


class SchemaString(Schema):
    """Schema container for 'string' type."""

    @staticmethod
    def for_type() -> str:
        """Get the 'type' key value that should map for this Schema object."""
        return "string"

    def parse_value(self, value: Any) -> Optional[str]:
        """Parse the supplied value into a string."""
        is_pre_parsed, parsed = self.parse_pre(value=value)
        if not is_pre_parsed:
            if not is_str(value=parsed) and self.required:
                self.error(
                    f"Value is required, must be a non-empty string, not {self.vinfo(value)}"
                )

            if self.format_is_email and not is_email(value=value):
                self.error(f"Value must be a valid email: {self.vinfo(value)}")

            self.resolved(value=value, parsed=parsed, reason="string")
            self.check_enum(value=parsed)
        return parsed

    @property
    def format_is_email(self) -> bool:
        """See if :attr:`format` == 'email'."""
        return self.format == "email"


def get_schemas_str(schemas: List[Schema]) -> str:
    """Build a string describing all schemas for an adapter."""
    items = []
    required = []
    optional = []
    for schema in schemas:
        target = required if schema.required else optional
        target.append(schema.name)
        items.append(repr(schema))

    barrier = "\n{}\n".format("-" * 60)
    items = [
        barrier,
        barrier.join(items),
        "\n",
        f"Required schemas: {', '.join(required)}",
        "\n",
        f"Optional schemas: {', '.join(optional)}",
    ]
    ret = "".join(items)
    return ret


def get_defaults_sane(adapter_name: str) -> dict:
    """Build a dict with the sane defaults for connections for adapter_name."""
    return CNX_SANE_DEFAULTS.get(adapter_name, CNX_SANE_DEFAULTS["all"])


def get_defaults_schemas(schemas: List[dict]) -> dict:
    """Build a dict with the defaults defined in schemas for cnxs."""
    return {x["name"]: x["default"] for x in schemas if "default" in x}


def get_defaults(adapter_name: str, schemas: List[dict]) -> dict:
    """Build a dict with defaults, sane defaults, required, and optionals."""
    sane = get_defaults_sane(adapter_name=adapter_name)
    sane = {k: v for k, v in sane.items() if k in [x["name"] for x in schemas]}

    schema_defaults = get_defaults_schemas(schemas=schemas)

    required = []
    optional = []
    for schema in schemas:
        target = required if schema["required"] else optional
        target.append(schema["name"])
        if schema["type"] == "bool":
            sane.setdefault(schema["name"], SchemaBool.SANE_DEFAULT)

    return {
        "required": required,
        "optional": optional,
        "schema_defaults": schema_defaults,
        "sane_defaults": sane,
    }


def get_defaults_str(adapter_name: str, schemas: List[dict]) -> str:
    """Build a str with defaults, sane defaults, required, and optionals."""

    def get_v(value):
        if isinstance(value, dict):
            return "\n  " + "\n  ".join(join_kv(value)) if value else "NO DEFAULTS..."
        return value

    data = get_defaults(adapter_name=adapter_name, schemas=schemas)
    return "\n".join([f"{k}: {get_v(v)}" for k, v in data.items()])


def get_show_data(
    adapter_name: str,
    schemas: List[dict],
    show_schemas: bool = Defaults.show_schemas,
    show_defaults: bool = Defaults.show_defaults,
    use_sane_defaults: bool = Defaults.use_sane_defaults,
) -> Optional[str]:
    """Get schemas or defaults strs."""
    if show_schemas:
        schemas = Schema.load_types(
            schemas=schemas,
            adapter_name=adapter_name,
            use_sane_defaults=use_sane_defaults,
        )
        return get_schemas_str(schemas)

    if show_defaults:
        return get_defaults_str(adapter_name=adapter_name, schemas=schemas)

    return None


def handle_unknowns(
    schemas: List[Schema],
    config: dict,
    ignore_unknowns: bool = Defaults.ignore_unknowns,
    error_as_exc: bool = Defaults.error_as_exc,
):
    """Check for unknown keys in config."""
    names = [x.name for x in schemas]
    unknowns = {k: v for k, v in config.items() if k not in names}

    if unknowns:
        unknowns_str = "\n  " + "\n  ".join(join_kv(unknowns))
        errs = [f"Unknown config keys supplied:{unknowns_str}"]
        msg = "\n".join([*errs, "", get_schemas_str(schemas), "", *errs])
        echo_error(msg=msg, abort=not ignore_unknowns and not error_as_exc)
        if not ignore_unknowns and error_as_exc:
            raise SchemaError(msg)


def parse_config(
    schemas: List[dict],
    adapter_name: str,
    config: dict,
    config_previous: Optional[dict] = None,
    use_sane_defaults: bool = Defaults.use_sane_defaults,
    prompt_for_previous: bool = Defaults.prompt_for_previous,
    prompt_for_optional: bool = Defaults.prompt_for_optional,
    prompt_for_default: bool = Defaults.prompt_for_default,
    prompt_for_missing_required: bool = Defaults.prompt_for_missing_required,
    ignore_unknowns: bool = Defaults.ignore_unknowns,
    error_as_exc: bool = Defaults.error_as_exc,
) -> dict:
    """Parse a supplied config and prompt for any unsupplied items."""
    schemas = Schema.load_types(
        schemas=schemas,
        adapter_name=adapter_name,
        use_sane_defaults=use_sane_defaults,
        prompt_for_optional=prompt_for_optional,
        prompt_for_default=prompt_for_default,
        prompt_for_missing_required=prompt_for_missing_required,
        prompt_for_previous=prompt_for_previous,
        error_as_exc=error_as_exc,
    )
    echo_debug(f"Supplied config keys {list(config)}")
    echo_debug(f"Supplied previous config keys {list(config_previous or {})}")
    echo_debug(f"All schema keys: {[x.name for x in schemas]}")

    handle_unknowns(
        schemas=schemas, config=config, ignore_unknowns=ignore_unknowns, error_as_exc=error_as_exc
    )
    ret = {x.name: x.parse(config=config, config_previous=config_previous) for x in schemas}
    return ret
