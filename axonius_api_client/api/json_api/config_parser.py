# -*- coding: utf-8 -*-
"""Parsers for configuration schemas."""
import dataclasses
import logging
import textwrap
from typing import Any, Callable, List, Optional, Union

import click
import tabulate

from ...connect import Connect
from ...constants.api import SANE_SCHEMA_DEFAULTS
from ...constants.general import NO, YES
from ...constants.logs import LOG_LEVEL_PARSE
from ...exceptions import ConfigInvalidValue, ConfigUnknown
from ...logs import get_obj_log
from ...tools import echo, listify
from .instances import Instance

# XXX adapters.cnx.destroy(adapter_name, adapter_node, destory)
# XXX dashboards.wait_data_stable()
# XXX dashboards.set_schedule(dialy/hourly/etc)
# XXX default bools to false??? default_bool: Optional[bool] = None
# XXX saved query update
# XXX  cnx.discover schedule
# if isinstance bool use it
# XXX instance needs a sane default :)
# if all optional, prompt for everything
# array types... fml


def wrap(value: str, pre: str, width: int = 30) -> str:
    """Pass."""
    new_value = textwrap.fill(value, width=width)
    return f"{pre}{new_value}"


def fill_list(
    value: List[str], pre: str, indent: int = 2, fill: str = " ", bullet: str = " - "
) -> str:
    """Pass."""
    if indent is None:
        indent_txt = ""
    elif isinstance(indent, int):
        indent_txt = fill * indent if indent else fill * len(pre)

    new_value = listify(obj=value)
    new_value = [f"{indent_txt}{bullet}{x}" for x in new_value]
    new_value = ["", *new_value, ""]
    new_value = "\n".join(new_value)
    return f"{pre}{new_value}"


@dataclasses.dataclass
class ConfigStore:
    """Pass."""

    parser: "ConfigParser"
    new: dict = dataclasses.field(default_factory=dict)
    old: dict = dataclasses.field(default_factory=dict)
    parsed: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        self.new = self.new or {}
        self.old = self.old or {}
        self.parsed = self.parsed or {}

    def check_unknown(self):
        """Pass."""
        # XXX for parents, check if all keys known
        for k, v in self.new.items():
            if k not in self.parser.valid_keys:
                msg = f"Unknown configuration key supplied {k!r}"
                if self.parser.prompt_ignore_unknown:
                    echo(
                        msg=f"Ignoring {msg}",
                        warning=True,
                        logger=self.parser.LOG,
                        console=self.parser.prompt_values,
                    )
                else:
                    msg = self.parser.get_table(err=msg)
                    echo(
                        msg=msg,
                        error=True,
                        exc=ConfigUnknown,
                        logger=self.parser.LOG,
                        console=self.parser.prompt_values,
                    )

    def get_value_old(self, schema: "ConfigSchema") -> Any:
        """Pass."""
        if schema.parent:
            if schema.parent.name in self.old:
                if schema.name in self.old[schema.parent.name]:
                    return self.old[schema.parent.name][schema.name]

        if schema.name in self.old:
            return self.old[schema.name]

        return None

    def get_value_new(self, schema: "ConfigSchema") -> Any:
        """Pass."""
        if schema.parent:
            if schema.parent.name in self.new:
                if schema.name in self.new[schema.parent.name]:
                    return self.new[schema.parent.name][schema.name]

        if schema.name in self.new:
            return self.new[schema.name]

        return None

    def has_value_old(self, schema: "ConfigSchema") -> bool:
        """Pass."""
        if schema.parent:
            if schema.parent.name in self.old:
                if schema.name in self.old[schema.parent.name]:
                    return True

        if schema.name in self.old:
            return True

        return False

    def has_value_new(self, schema: "ConfigSchema") -> bool:
        """Pass."""
        if schema.parent:
            if schema.parent.name in self.new:
                if schema.name in self.new[schema.parent.name]:
                    return True

        if schema.name in self.new:
            return True

        return False

    def set_value(self, schema: "ConfigSchema", value: Any):
        """Pass."""
        if schema.parent:
            if schema.parent.name not in self.parsed:
                self.parsed[schema.parent.name] = {}
            self.parsed[schema.parent.name][schema.name] = value
        else:
            self.parsed[schema.name] = value


@dataclasses.dataclass
class ConfigSchema:
    """Pass."""

    schema: dict
    parser: "ConfigParser"
    idx: int = 0
    parent: Optional["ConfigSchema"] = None

    @property
    def name(self) -> str:
        """Pass."""
        return self.schema["name"]

    @property
    def type(self) -> str:
        """Pass."""
        return self.schema["type"]

    @property
    def format(self) -> str:
        """Pass."""
        return self.schema.get("format", "")

    @property
    def description(self) -> str:
        """Pass."""
        return self.schema.get("description", "")

    @property
    def title(self) -> str:
        """Pass."""
        return self.schema.get("title", "")

    @property
    def enum(self) -> List[Union[str, int, float, dict]]:
        """Pass."""
        return self.schema.get("enum", [])

    @property
    def items(self) -> List[dict]:
        """Pass."""
        return self.schema.get("items", [])

    @property
    def items_required(self) -> List[str]:
        """Pass."""
        return self.schema.get("required", [])

    @property
    def max_length(self) -> Optional[int]:
        """Pass."""
        if "limit" in self.schema:
            return self.schema["limit"]

        return None

    @property
    def minimum(self) -> Optional[int]:
        """Pass."""
        if "min" in self.schema:
            return self.schema["min"]

        if "minimum" in self.schema:
            return self.schema["minimum"]

        return None

    @property
    def maximum(self) -> Optional[int]:
        """Pass."""
        if "max" in self.schema:
            return self.schema["max"]

        if "maximum" in self.schema:
            return self.schema["maximum"]

        return None

    @property
    def _is_required(self) -> bool:
        """Pass."""
        if self.name in self.parser.requireds:
            return True

        if self.schema.get("required"):
            return True

        if self.parent and self.name in self.parent.schema.get("required", []):
            return True

        return False

    @property
    def required(self) -> bool:
        """Pass."""
        if self._is_required and self.default_value in [None, ""]:
            return True

        return False

    @property
    def default_value(self) -> Any:
        """Pass."""
        if self.name == "instance":
            return self.parser.core_instance.name

        if "default" in self.schema:
            return self.schema["default"]

        if self.parent and "default" in self.parent.schema:
            return self.parent.schema["default"]

        if self.name in self.parser.defaults:
            return self.parser.defaults[self.name]

        if self.name in self.parser.defaults_sane_all:
            return self.parser.defaults_sane_all[self.name]

        if self.name in self.parser.defaults_sane:
            return self.parser.defaults_sane[self.name]

        if self.type == "bool" and isinstance(self.parser.defaults_bool, bool):
            return self.parser.defaults_bool

        return None

    @property
    def default_defined(self) -> bool:
        """Pass."""
        if self.name == "instance":
            return True

        if "default" in self.schema:
            return True

        if self.parent and "default" in self.parent.schema:
            return True

        if self.name in self.parser.defaults:
            return True

        if self.name in self.parser.defaults_sane_all:
            return True

        if self.name in self.parser.defaults_sane:
            return True

        if self.type == "bool" and isinstance(self.parser.defaults_bool, bool):
            return True

        return False

    @property
    def valid_keys(self) -> List[str]:
        """Pass."""
        ret = [self.name, *[x.name for x in self.sub_schemas]]
        if self.type == "file":
            ret += [f"{self.name}_filename", f"{self.name}_uuid", f"{self.name}_filepath"]
        return ret

    @property
    def sub_schemas(self) -> List["ConfigSchema"]:
        """Pass."""

        def get_cp(idx, item):
            return ConfigSchema(schema=item, parser=self.parser, parent=self, idx=idx)

        if not hasattr(self, "_sub_schemas"):
            self._sub_schemas = []
            if self.type == "array" and self.items:
                items = [x for x in self.items if isinstance(x, dict)]
                self._sub_schemas = [get_cp(idx=idx, item=x) for idx, x in enumerate(items)]
        return self._sub_schemas

    @property
    def conditional_children(self) -> List[str]:
        """Pass."""
        ret = []
        for enum in self.enum:
            if not isinstance(enum, dict) or self.parent:
                continue

            name = enum.get("name")

            if name and isinstance(name, str):
                ret.append(name)

        return ret

    @property
    def conditional_parent(self) -> str:
        """Pass."""
        for schema in self.parser._items:
            enums = schema.get("enum", [])
            for enum in enums:
                if not (isinstance(enum, dict) and "name" in enum):
                    continue

                if self.name == enum["name"]:
                    return schema["name"]

        if self.parent and self.parent.conditional_parent:
            return self.parent.conditional_parent

        return ""

    def parse_bool(self, store: ConfigStore) -> ConfigStore:
        """Pass."""
        do_prompt = False
        if store.has_value_new(schema=self):
            value = store.get_value_new(schema=self)
            default_src = "supplied value"
        elif store.has_value_old(schema=self):
            value = store.get_value_old(schema=self)
            default_src = "previous value"
            if self.parser.prompt_old:
                do_prompt = True
        elif self.default_defined:
            value = self.default_value
            default_src = "default value"
            if self.parser.prompt_default:
                do_prompt = True
        else:
            value = None
            default_src = ""
            do_prompt = True

        print(f"value from {default_src} {value!r}")

        if do_prompt and self.parser.prompt_values:
            table = tabulate.tabulate([self.to_tablize()], tablefmt="fancy_grid", headers="keys")
            text = f"Enter boolean value for {self.name}"

            if default_src:
                text = f"{text} (default from {default_src})"

            text = "\n".join([table, "", text])

            value = click.prompt(
                text=text,
                default=value,
                type=click.BOOL,
                err=True,
                show_default=True,
                show_choices=True,
            )

        value = value.lower().strip() if isinstance(value, str) else value

        if value in YES:
            value = True
        elif value in NO:
            value = False
        else:
            msg = self._msg_invalid_value(value=value)
            raise ConfigInvalidValue(msg)

        store.set_value(schema=self, value=value)
        return store

    def parse(self, store: ConfigStore) -> ConfigStore:
        """Pass."""
        if self.type == "bool":
            self.parse_bool(store)
        return store

    def to_tablize(self) -> dict:
        """Pass."""
        ret = {}
        ret["Configuration Key"] = self.name
        ret["Details"] = "\n".join(self._msg_details())
        return ret

    @property
    def _str_properties(self) -> List[str]:
        """Pass."""
        return [
            "name",
            "title",
            "type",
            "required",
            "default_defined",
            "default_value",
        ]

    def __str__(self) -> str:
        """Pass."""
        items = {x.replace("_", " ").title(): getattr(self, x) for x in self._str_properties}
        items = [f"{k}: {v!r}" for k, v in items.items()]
        return ", ".join(items)

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()

    def _msg_invalid_value(self, value: Any) -> str:
        """Pass."""
        vtype = type(value).__name__
        src = self.parser.source

        err = f"Error: Invalid value type supplied for configuration key {self.name!r}"
        correct = f"Supplied value {value!r} of type {vtype!r} must be type: {self.type!r}"
        errs = [err, f"From schema for {src}", ""]

        if self.type == "bool":
            yes = ", ".join(sorted(list(set([str(x) for x in YES]))))
            no = ", ".join(sorted(list(set([str(x) for x in NO]))))
            errs += [
                correct,
                f"Valid values for true: {yes}",
                f"Valid values for false: {no}",
            ]
        else:
            errs += ["", correct]

        table = tabulate.tabulate([self.to_tablize()], tablefmt="fancy_grid", headers="keys")
        errs += ["", table]
        return "\n".join(errs)

    def _msg_details(self) -> List[str]:
        """Pass."""
        ret = []
        ret += [wrap(value=self.title, pre="Title: "), ""]

        if self.description:
            ret += [wrap(value=self.description, pre="Description: "), ""]

        ret.append(f"Type: {self.type}")

        if self.format:
            ret.append(f"Format: {self.format}")

        if self.default_defined and not self.required:
            ret.append(f"Default: {self.default_value!r}")

        ret.append(f"Required: {self.required}")

        if self.conditional_parent:
            pre = "Only usable if: "
            if self.parent:
                post = f"{self.conditional_parent}={self.parent.name}"
            else:
                post = f"{self.conditional_parent}={self.name}"
            ret += [pre, f"  {post}", ""]

        if self.conditional_children:
            pre = "Conditional Values: "
            valid = [repr(x) for x in self.conditional_children]
            ret += [fill_list(value=valid, pre=pre), ""]

        if self.enum and all([isinstance(x, (str, int, float)) for x in self.enum]):
            pre = "Valid Values: "
            valid = [repr(x) for x in self.enum]
            ret += [fill_list(value=valid, pre=pre), ""]

        if self.max_length is not None:
            ret.append(f"Maximum length: {self.max_length}")

        if self.minimum is not None:
            ret.append(f"Minimum: {self.minimum}")

        if self.maximum is not None:
            ret.append(f"Maximum: {self.maximum}")

        return ret


class ConfigParser:
    """Pass."""

    def __init__(
        self,
        client: Connect,
        schema: dict,
        defaults: Optional[dict] = None,
        defaults_sane: Optional[dict] = None,
        defaults_sane_key: str = "",
        source: str = "",
        file_upload_cb: Optional[Callable] = None,
        prompt_values: bool = True,
        prompt_ignore_unknown: bool = False,  # --prompt-ignore-unknown/--no-prompt-ignore-unknown
        prompt_optional: bool = True,  # --prompt-optionals / --no-prompt-optionals
        prompt_default: bool = True,  # --prompt-defaults / --no-prompt-defaults
        prompt_old: bool = False,  # --prompt-previous-values/--no-prompt-previous-values
        defaults_bool: Optional[bool] = False,  # --default-for-bool None/yes/no
        **kwargs,
    ):
        """Pass."""
        log_level: Union[int, str] = kwargs.get("log_level", LOG_LEVEL_PARSE)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.client: Connect = client

        self._schema = schema
        self._file_upload_cb: Callable = file_upload_cb
        self._defaults_sane: dict = defaults_sane or SANE_SCHEMA_DEFAULTS
        self._defaults_sane_key: str = defaults_sane_key
        self.defaults: dict = defaults or {}
        self.source: str = source
        self.prompt_values = prompt_values
        self.prompt_ignore_unknown = prompt_ignore_unknown
        self.prompt_optional = prompt_optional
        self.prompt_default = prompt_default
        self.prompt_old = prompt_old
        self.defaults_bool = defaults_bool

    @property
    def defaults_sane_all(self) -> dict:
        """Pass."""
        return self._defaults_sane.get("*", {})

    @property
    def defaults_sane(self) -> dict:
        """Pass."""
        return self._defaults_sane.get(self._defaults_sane_key, {})

    @property
    def core_instance(self) -> Instance:
        """Pass."""
        for instance in self.client.instances.get_cached():
            if instance.is_master:
                return instance

    def parse(self, old: Optional[dict] = None, new: Optional[dict] = None) -> dict:
        """Pass."""
        # --config key=value
        store = ConfigStore(new=new, old=old, parser=self)
        store.check_unknown()
        for schema in self.schemas:
            schema.parse(store=store)

        return store

    def to_tablize(self) -> List[dict]:
        """Pass."""
        req = []
        opt = []
        subs = []
        for schema in self.schemas:
            subs += schema.sub_schemas

            if schema.sub_schemas and schema.conditional_parent:
                continue

            req.append(schema) if schema.required else opt.append(schema)
        return [x.to_tablize() for x in req + opt + subs]

    def get_table(self, fmt: str = "fancy_grid", err: str = "") -> str:
        """Pass."""
        tables = self.to_tablize()
        if tables:
            value = tabulate.tabulate(tables, tablefmt=fmt, headers="keys")
        else:
            value = "-- No configuration keys defined"

        err = f"Error: {err}\n" if err else ""
        desc = f"{err}Valid configuration keys for {self.source}\n"
        return "\n".join([desc, value, "", err])

    @property
    def requireds(self) -> List[str]:
        """Pass."""
        return self._schema.get("required", [])

    @property
    def schemas(self) -> List[ConfigSchema]:
        """Pass."""
        if not getattr(self, "_schemas", None):
            self._schemas = [
                ConfigSchema(schema=x, parser=self, idx=idx) for idx, x in enumerate(self._items)
            ]

        return self._schemas

    @property
    def _items(self) -> List[str]:
        """Pass."""
        if isinstance(self._schema, dict):
            return self._schema.get("items", [])
        return []

    @property
    def _names(self) -> List[str]:
        """Pass."""
        return [x["name"] for x in self._items]

    @property
    def valid_keys(self):
        """Pass."""
        return [y for x in self.schemas for y in x.valid_keys]
