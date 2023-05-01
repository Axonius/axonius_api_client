# -*- coding: utf-8 -*-
"""Parsers for configuration schemas."""
import copy
import pathlib
from typing import Any, List, Optional, Tuple, Union

from ..constants.api import SETTING_UNCHANGED
from ..constants.general import NO, YES
from ..exceptions import (
    ApiError,
    ConfigInvalidValue,
    ConfigRequired,
    ConfigUnchanged,
    ConfigUnknown,
)
from ..tools import coerce_int, is_int, join_kv, json_load
from .tables import tablize_schemas

HIDDEN_KEYS = ["secret", "key", "password"]


def config_check(
    value: str,
    schema: dict,
    source: str,
    callbacks: Optional[dict] = None,
    none_ok: bool = True,
) -> Any:
    """Check a supplied value for a setting is correctly typed.

    Args:
        value: value supplied by user
        schema: configuration schema to use to validate value
        source: identifier of where value came from
        callbacks: callback operations to run for this value
        none_ok: Empty values are ok

    Raises:
        :exc:`ApiError`: If the supplied schema has an unknown type
        :exc:`ConfigInvalidValue`: if none_ok is false and value is None or "None"
    """
    schema_type = schema["type"]

    if value is None or str(value).strip().lower() == "none":
        if none_ok:
            return None
        else:
            sinfo = config_info(schema=schema, value=value, source=source)
            raise ConfigInvalidValue(f"{sinfo}\nValue of {value!r} not allowed")

    if schema_type == "file":
        return config_check_file(value=value, schema=schema, callbacks=callbacks, source=source)

    if schema_type == "bool":
        return config_check_bool(value=value, schema=schema, callbacks=callbacks, source=source)

    if schema_type == "number":
        return config_check_int(value=value, schema=schema, callbacks=callbacks, source=source)

    if schema_type == "integer":
        return config_check_int(value=value, schema=schema, callbacks=callbacks, source=source)

    if schema_type == "array":
        return config_check_array(value=value, schema=schema, callbacks=callbacks, source=source)

    if schema_type == "string":
        return config_check_str(value=value, schema=schema, callbacks=callbacks, source=source)

    valids = ["string", "integer", "number", "bool", "array"]
    valids = ", ".join(valids)
    raise ApiError(f"Schema type {schema_type!r} is unknown, valids: {valids}")


def config_check_file(
    value: Union[str, dict, pathlib.Path],
    schema: dict,
    source: str,
    callbacks: Optional[dict] = None,
) -> dict:
    """Check a supplied value for a schema of type file.

    Args:
        value: value supplied by user
        schema: configuration schema to use to validate value
        source: identifier of where value came from
        callbacks: callback operations to run for this value

    Raises:
        :exc:`ApiError`: If the supplied schema does not have a callback
    """
    sname = schema["name"]

    callbacks = callbacks or {}
    cb_file = callbacks.get("cb_file", None)

    is_file, value = is_uploaded_file(value=value)
    if is_file:
        return value

    if callable(cb_file):
        return cb_file(value=value, schema=schema, callbacks=callbacks, source=source)

    raise ApiError(f"File uploads for {source} setting {sname!r} are not supported yet")


def config_check_bool(
    value: Union[str, bool, int],
    schema: dict,
    source: str,
    callbacks: Optional[dict] = None,
) -> bool:
    """Check a supplied value for a schema of type boolean.

    Args:
        value: value supplied by user
        schema: configuration schema to use to validate value
        source: identifier of where value came from
        callbacks: callback operations to run for this value

    Raises:
        :exc:`ConfigInvalidValue`: if the supplied value is not a valid boolean
    """
    coerce = value.lower().strip() if isinstance(value, str) else value

    if coerce in YES:
        return True

    if coerce in NO:
        return False

    sinfo = config_info(schema=schema, value=value, source=source)

    yes = ", ".join(sorted([str(x) for x in YES]))
    no = ", ".join(sorted([str(x) for x in NO]))
    msg = [
        sinfo,
        "Is not a valid boolean!",
        f"Valid values for true: {yes}",
        f"Valid values for false: {no}",
    ]
    raise ConfigInvalidValue("\n".join(msg))


def config_check_int(
    value: Union[str, int], schema: dict, source: str, callbacks: Optional[dict] = None
) -> int:
    """Check a supplied value for a schema of integer.

    Args:
        value: value supplied by user
        schema: configuration schema to use to validate value
        source: identifier of where value came from
        callbacks: callback operations to run for this value

    Raises:
        :exc:`ConfigInvalidValue`: if the supplied value is not an integer
    """
    if is_int(obj=value, digit=True):
        return coerce_int(
            obj=value, max_value=schema.get("max", None), min_value=schema.get("min", None)
        )

    sinfo = config_info(schema=schema, value=value, source=source)
    raise ConfigInvalidValue(f"{sinfo}\nIs not a valid integer!")


def config_check_array(
    value: Union[str, List[str]],
    schema: dict,
    source: str,
    callbacks: Optional[dict] = None,
) -> List[str]:
    """Check a supplied value for a schema of type array.

    Args:
        value: value supplied by user
        schema: configuration schema to use to validate value
        source: identifier of where value came from
        callbacks: callback operations to run for this value

    Raises:
        :exc:`ConfigInvalidValue`: if the supplied value is not a CSV string or a list of strings
    """
    if isinstance(value, str):
        value = [x.strip() for x in value.split(",") if x.strip()]

    is_list = isinstance(value, list)

    if not is_list or (is_list and not all([isinstance(x, str) for x in value])):
        sinfo = config_info(schema=schema, value=value, source=source)
        msg = f"{sinfo}\nIs not a list of strings or a comma seperated string!"
        raise ConfigInvalidValue(msg)

    return value


def parse_unchanged(value: Union[str, List[str]]) -> Tuple[bool, Union[str, List[str]]]:
    """Determine if a value is 'unchanged'.

    Args:
        value: value supplied by user
    """
    unchanges = [
        SETTING_UNCHANGED,
        str(SETTING_UNCHANGED),
        SETTING_UNCHANGED[0],
        str(SETTING_UNCHANGED[0]),
    ]
    if value in unchanges:
        return True, SETTING_UNCHANGED
    return False, value


def config_check_str(
    value: str, schema: dict, source: str, callbacks: Optional[dict] = None
) -> str:
    """Check a supplied value for a schema of type string.

    Args:
        value: value supplied by user
        schema: configuration schema to use to validate value
        source: identifier of where value came from
        callbacks: callback operations to run for this value

    Raises:
        :exc:`ConfigInvalidValue`: if the supplied value is not a string or if the schema
            has enums and the supplied value is not one of the enums
    """
    schema_fmt = schema.get("format", "")
    schema_enum = schema.get("enum", [])

    if schema_enum:
        enum_is_str = all([isinstance(x, str) for x in schema_enum])
        if enum_is_str:
            if value not in schema_enum:
                sinfo = config_info(schema=schema, value=value, source=source)
                raise ConfigInvalidValue(f"{sinfo}\nIs not one of {schema_enum}!")
        else:  # pragma: no cover
            valids = [x["name"] for x in schema_enum]
            if value not in valids:
                valids = "\n" + "\n".join(["  ".join(x) for x in join_kv(obj=schema_enum)])
                sinfo = config_info(schema=schema, value=value, source=source)
                raise ConfigInvalidValue(f"{sinfo}\nIs not one of:{valids}!")

    if schema_fmt == "password":
        parsed, value = parse_unchanged(value=value)
        if parsed:
            return value

    value = str(value) if isinstance(value, int) else value

    if not isinstance(value, str):
        sinfo = config_info(schema=schema, value=value, source=source)
        raise ConfigInvalidValue(f"{sinfo}\nIs not a string!")

    return value


def config_build(
    schemas: List[dict],
    old_config: dict,
    new_config: dict,
    source: str,
    check: bool = True,
    callbacks: Optional[dict] = None,
) -> dict:
    """Build a configuration from a new config and an old config.

    Args:
        schemas: schemas to validate against key value pairs in new_config
        old_config: previous configuration
        new_config: new configuration supplied by user
        source: identifier of where new_config came from
        callbacks: callback operations to use for schemas
    """
    for name, schema in schemas.items():
        if name not in new_config and name in old_config:
            new_config[name] = old_config[name]
        elif name in new_config:
            value = new_config[name]
            if check:  # pragma: no cover
                value = config_check(value=value, schema=schema, source=source, callbacks=callbacks)
            new_config[name] = value
    return new_config


def config_unknown(
    schemas: List[dict], new_config: dict, source: str, callbacks: Optional[dict] = None
) -> dict:
    """Check that keys in the supplied configuration are known to the schemas for a connection.

    Args:
        schemas: schemas to validate against key value pairs in new_config
        new_config: new configuration supplied by user
        source: identifier of where new_config came from
        callbacks: callback operations to use for schemas

    Raises:
        :exc:`ConfigUnknown`: if the supplied new config has unknown keys to the schemas
    """
    unknowns = {k: v for k, v in new_config.items() if k not in schemas}

    if unknowns:
        unknowns = ["{}: {!r}".format(k, v) for k, v in unknowns.items()]
        unknowns = "\n  " + "\n  ".join(unknowns)
        err = f"Unknown settings supplied for {source}: {unknowns}"
        raise ConfigUnknown(tablize_schemas(schemas=schemas, err=err))
    return new_config


def config_unchanged(
    schemas: List[dict],
    old_config: dict,
    new_config: dict,
    source: str,
    callbacks: Optional[dict] = None,
) -> dict:
    """Check if a new config is different from the old config.

    Args:
        schemas: schemas to validate against key value pairs in new_config
        old_config: previous configuration
        new_config: new configuration supplied by user
        source: identifier of where new_config came from
        callbacks: callback operations to use for schemas

    Raises:
        :exc:`ConfigUnchanged`: if the supplied new config is empty or is not different from old
            config
    """
    if new_config == old_config or not new_config:
        err = f"No changes supplied for {source}"
        raise ConfigUnchanged(tablize_schemas(schemas=schemas, config=old_config, err=err))
    return new_config


def config_default(
    schemas: List[dict],
    new_config: dict,
    source: str,
    sane_defaults: Optional[dict] = None,
    callbacks: Optional[dict] = None,
) -> dict:
    """Set defaults for a supplied config.

    Args:
        schemas: schemas to validate against key value pairs in new_config
        new_config: new configuration supplied by user
        source: identifier of where new_config came from
        callbacks: callback operations to use for schemas
        sane_defaults: set of sane defaults provided by API client to use in addition to defaults
            defined in schemas
    """
    sane_defaults = sane_defaults or {}

    for name, schema in schemas.items():
        if name in new_config:
            continue

        if "default" in schema:
            new_config[name] = schema["default"]

        if name in sane_defaults:
            new_config[name] = sane_defaults[name]

    return new_config


def config_required(
    schemas: List[dict],
    new_config: dict,
    source: str,
    ignores: Optional[List[str]] = None,
    callbacks: Optional[dict] = None,
) -> dict:
    """Check if a new config has all required keys.

    Args:
        schemas: schemas to validate against key value pairs in new_config
        new_config: new configuration supplied by user
        source: identifier of where new_config came from
        ignores: schema keys to ignore
        callbacks: callback operations to use for schemas

    Raises:
        :exc:`ConfigRequired`: if the supplied new config is empty or is not different from old
            config
    """
    missing = []
    ignores = ignores or []
    for name, schema in schemas.items():
        if schema["required"] and name not in new_config and name not in ignores:
            missing.append(schema)

    if missing:
        err = f"Required configurations not supplied for {source}"
        raise ConfigRequired(tablize_schemas(schemas=missing, err=err))
    return new_config


def config_empty(
    schemas: List[dict], new_config: dict, source: str, callbacks: Optional[dict] = None
) -> dict:
    """Check if a new config is empty.

    Args:
        schemas: schemas to validate against key value pairs in new_config
        new_config: new configuration supplied by user
        source: identifier of where new_config came from
        ignores: schema keys to ignore
        callbacks: callback operations to use for schemas

    Raises:
        :exc:`ConfigRequired`: if the supplied new config is empty or is not different from old
            config
    """
    if not new_config:
        err = f"No configuration supplied for {source}"
        raise ConfigRequired(tablize_schemas(schemas=schemas, err=err))
    return new_config


def config_info(schema: dict, value: Any, source: str) -> str:
    """Get a string repr of the schema and value.

    Args:
        value: user supplied value
        schema: config schema associated with value
        source: identifier of where value came from

    """
    value_type = type(value).__name__
    return (
        f"Value {value!r} of type {value_type!r} "
        f"supplied for {source} setting {schema['name']!r}"
    )


def is_uploaded_file(value: Union[str, dict]) -> Tuple[bool, Union[str, dict]]:
    """Determine if value is a previously uploaded file.

    Args:
        value: value supplied by user
    """
    check = value

    if isinstance(check, str):
        check = json_load(obj=value, error=False)

    if isinstance(check, dict):
        uuid = check.get("uuid")
        filename = check.get("filename")
        values = [uuid, filename]
        if all(values) and all([isinstance(x, str) for x in values]):
            return True, check
    return False, value


def parse_schema(raw: dict) -> dict:
    """Parse a field, adapter, or config schema into a more user-friendly format.

    Args:
        raw: original schema
    """
    if not raw:  # pragma: no cover
        return {}

    parsed = {}
    schemas = raw["items"]
    required = raw["required"]

    for schema in schemas:
        name = schema["name"]
        schema["required"] = name in required
        schema["hide_value"] = (
            schema.get("format", "") == "password" or schema["name"] in HIDDEN_KEYS
        )
        parsed[name] = schema

    return parsed


def parse_schema_enum(schema: dict):
    """Parse a field, adapter, or config schema into a more user-friendly format.

    Args:
        raw: original schema
    """
    # core settings: password_brute_force_protection: conditional
    # has a list of dict enums, so turn it into a lookup map
    if schema.get("enum") and isinstance(schema["enum"][0], dict):
        schema["enum"] = {x["name"]: x for x in schema["enum"]}


# TBD: re-tool to return cleaned up 'raw'
def parse_section(raw: dict, raw_config: dict, parent: dict, settings: dict) -> dict:
    """Parse a section of system settings into a more user-friendly format."""
    # FYI has no title:
    #   settings_gui::saml_login_settings::configure_authncc
    title = raw.get("title", raw["name"].replace("_", " ").title())
    config = raw_config.get(raw["name"], {})
    section_name = raw["name"]
    schemas = raw["items"]
    # FYI core_settings::tunnel_email_recipients is missing 'required' as of 3.6!
    # required = raw["required"]
    required = raw.get("required", [])

    section_defaults = raw.get(section_name, {})

    parsed = {}
    parsed["settings_title"] = settings["settings_title"]
    parsed["name"] = section_name
    parsed["title"] = title
    parsed["schemas"] = {}
    parsed["sub_sections"] = sub_sections = {}
    parsed["parent_name"] = parent.get("name", "")
    parsed["parent_title"] = parent.get("title", "")
    parsed["config"] = config

    for schema in schemas:
        parse_schema_enum(schema=schema)
        schema_name = schema["name"]

        items = schema.get("items", None)

        # sub_sections:
        #   {"items": [{}], "required": [""], "type": "array"}
        # FYI core_settings::tunnel_email_recipients has an empty items list 3.6
        if isinstance(items, list) and items:
            sub_sections[schema_name] = parse_section(
                raw=schema,
                raw_config=config,
                parent=parsed,
                settings=settings,
            )
            schema.pop("items")

        # non sub_sections:
        #   no items key in schema
        #   {{"items": {"type": ""} "type": "array"}
        # FYI some things have a required key already that is a bool 3.6
        if not isinstance(schema.get("required", []), bool):
            schema["required"] = schema_name in required

        parsed["schemas"][schema_name] = schema

        # FYI does not follow schema for defaults:
        #   core settings::https_log_settings
        if schema_name in section_defaults and "default" not in schema:
            schema["default"] = section_defaults[schema_name]

        # FYI has no title:
        #   settings_gui::saml_login_settings::configure_authncc
        schema["title"] = schema.get("title", schema_name.replace("_", " ").title())

    return parsed


# TBD: re-tool to return cleaned up 'raw'
def parse_settings(raw: dict, title: str = "") -> dict:
    """Parse system settings into a more user friendly format."""
    # FYI missing pretty_name:
    #   settings_gui
    #   settings_lifecycle
    schema = raw["document_meta"]["schema"]
    title = schema.get("pretty_name", "") or title

    raw_config = raw["config"]
    raw_sections = schema["items"]

    parsed = {}
    parsed["settings_title"] = title
    parsed["sections"] = sections = {}
    parsed["config"] = copy.deepcopy(raw_config)

    for raw_section in raw_sections:
        section_name = raw_section["name"]
        sections[section_name] = parse_section(
            raw=raw_section, raw_config=raw_config, parent={}, settings=parsed
        )

    return parsed
