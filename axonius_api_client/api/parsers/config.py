# -*- coding: utf-8 -*-
"""API models for working with adapters and connections."""
import copy

from ...constants import NO, SETTING_UNCHANGED, YES
from ...exceptions import (
    ApiError,
    ConfigInvalidValue,
    ConfigRequired,
    ConfigUnchanged,
    ConfigUnknown,
)
from ...tools import is_int, json_load
from .tables import tablize_schemas


def config_check(value, schema, source, callbacks=None, none_ok=True):
    """Check a supplied value for a setting is correctly typed."""
    schema_type = schema["type"]

    if value is None or str(value).strip() == "None":
        if none_ok:
            return None
        else:
            sinfo = config_info(schema=schema, value=value, source=source)
            raise ConfigInvalidValue(f"{sinfo}\nValue of None not allowed")

    if schema_type == "file":
        return config_check_file(
            value=value, schema=schema, callbacks=callbacks, source=source
        )

    if schema_type == "bool":
        return config_check_bool(
            value=value, schema=schema, callbacks=callbacks, source=source
        )

    if schema_type == "number":
        return config_check_int(
            value=value, schema=schema, callbacks=callbacks, source=source
        )

    if schema_type == "integer":
        return config_check_int(
            value=value, schema=schema, callbacks=callbacks, source=source
        )

    if schema_type == "array":
        return config_check_array(
            value=value, schema=schema, callbacks=callbacks, source=source
        )

    if schema_type == "string":
        return config_check_str(
            value=value, schema=schema, callbacks=callbacks, source=source
        )

    valids = ["string", "integer", "number", "bool", "array"]
    valids = ", ".join(valids)
    raise ApiError(f"Schema type {schema_type!r} is unknown, valids: {valids}")


def config_check_file(value, schema, source, callbacks=None):
    """Pass."""
    sname = schema["name"]

    callbacks = callbacks or {}
    cb_file = callbacks.get("cb_file", None)

    is_file, value = is_uploaded_file(value=value)
    if is_file:
        return value

    if callable(cb_file):
        return cb_file(value=value, schema=schema, callbacks=callbacks, source=source)

    raise ApiError(f"File uploads for {source} setting {sname!r} are not supported yet")


def config_check_bool(value, schema, source, callbacks=None):
    """Pass."""
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


def config_check_int(value, schema, source, callbacks=None):
    """Pass."""
    if is_int(obj=value, digit=True):
        return int(value)

    sinfo = config_info(schema=schema, value=value, source=source)
    raise ConfigInvalidValue(f"{sinfo}\nIs not a valid integer!")


def config_check_array(value, schema, source, callbacks=None):
    """Pass."""
    if isinstance(value, str):
        value = [x.strip() for x in value.split(",") if x.strip()]

    is_list = isinstance(value, list)

    if not is_list or (is_list and not all([isinstance(x, str) for x in value])):
        sinfo = config_info(schema=schema, value=value, source=source)
        msg = f"{sinfo}\nIs not a list of strings or a comma seperated string!"
        raise ConfigInvalidValue(msg)

    return value


def parse_unchanged(value):
    """Pass."""
    unchanges = [
        SETTING_UNCHANGED,
        str(SETTING_UNCHANGED),
        SETTING_UNCHANGED[0],
        str(SETTING_UNCHANGED[0]),
    ]
    if value in unchanges:
        return True, SETTING_UNCHANGED
    return False, value


def config_check_str(value, schema, source, callbacks=None):
    """Pass."""
    schema_fmt = schema.get("format", "")
    schema_enum = schema.get("enum", [])

    # XXX enum can be a dict lookup, handle better
    if schema_enum and value not in schema_enum:
        sinfo = config_info(schema=schema, value=value, source=source)
        raise ConfigInvalidValue(f"{sinfo}\nIs not one of {schema_enum}!")

    if schema_fmt == "password":
        parsed, value = parse_unchanged(value=value)
        if parsed:
            return value

    if isinstance(value, int):
        value = str(value)

    if not isinstance(value, str):
        sinfo = config_info(schema=schema, value=value, source=source)
        raise ConfigInvalidValue(f"{sinfo}\nIs not a string!")

    return value


def config_build(schemas, old_config, new_config, source, check=True, callbacks=None):
    """Pass."""
    for name, schema in schemas.items():
        if name not in new_config and name in old_config:
            new_config[name] = old_config[name]
        elif name in new_config:
            value = new_config[name]
            if check:
                value = config_check(
                    value=value, schema=schema, source=source, callbacks=callbacks
                )
            new_config[name] = value
    return new_config


def config_unknown(schemas, new_config, source, callbacks=None):
    """Pass."""
    unknowns = {k: v for k, v in new_config.items() if k not in schemas}
    if unknowns:
        unknowns = ["{}: {!r}".format(k, v) for k, v in unknowns.items()]
        unknowns = "\n  " + "\n  ".join(unknowns)
        err = f"Unknown settings supplied for {source}: {unknowns}"
        raise ConfigUnknown(tablize_schemas(schemas=schemas, err=err))
    return new_config


def config_unchanged(schemas, old_config, new_config, source, callbacks=None):
    """Pass."""
    if new_config == old_config or not new_config:
        err = f"No changes supplied for {source}"
        raise ConfigUnchanged(
            tablize_schemas(schemas=schemas, config=old_config, err=err)
        )
    return new_config


def config_default(schemas, new_config, source, sane_defaults=None, callbacks=None):
    """Pass."""
    sane_defaults = sane_defaults or {}

    for name, schema in schemas.items():
        if name in new_config:
            continue

        if "default" in schema:
            new_config[name] = schema["default"]

        if name in sane_defaults:
            new_config[name] = sane_defaults[name]

    return new_config


def config_required(schemas, new_config, source, ignores=None, callbacks=None):
    """Pass."""
    missing = []
    ignores = ignores or []
    for name, schema in schemas.items():
        if schema["required"] and name not in new_config and name not in ignores:
            missing.append(schema)

    if missing:
        err = f"Required configurations not supplied for {source}"
        raise ConfigRequired(tablize_schemas(schemas=missing, err=err))
    return new_config


def config_empty(schemas, new_config, source, callbacks=None):
    """Pass."""
    if not new_config:
        err = f"No configuration supplied for {source}"
        raise ConfigRequired(tablize_schemas(schemas=schemas, err=err))
    return new_config


def config_info(schema, value, source):
    """Pass."""
    value_type = type(value).__name__
    return (
        f"Value {value!r} of type {value_type!r} "
        f"supplied for {source} setting {schema['name']!r}"
    )


def is_uploaded_file(value):
    """Pass."""
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


def parse_schema(raw):
    """Pass."""
    parsed = {}
    if not raw:
        return parsed

    schemas = raw["items"]
    required = raw["required"]

    for schema in schemas:
        schema_name = schema["name"]
        parsed[schema_name] = schema
        schema["required"] = schema_name in required

    return parsed


def parse_schema_enum(schema):
    """Pass."""
    # core settings: password_brute_force_protection: conditional
    # has a list of dict enums, so turn it into a lookup map
    if schema.get("enum") and isinstance(schema["enum"][0], dict):
        schema["enum"] = {x["name"]: x for x in schema["enum"]}


def parse_section(raw, raw_config, parent, settings):
    """Pass."""
    # XXX has no title:
    #   settings_gui::saml_login_settings::configure_authncc
    title = raw.get("title", raw["name"].replace("_", " ").title())
    config = raw_config.get(raw["name"], {})
    section_name = raw["name"]
    schemas = raw["items"]
    required = raw["required"]
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
        if isinstance(items, list):
            sub_sections[schema_name] = parse_section(
                raw=schema, raw_config=config, parent=parsed, settings=settings,
            )
            schema.pop("items")

        # non sub_sections:
        #   no items key in schema
        #   {"items": {"type": ""} "type": "array"}
        schema["required"] = schema_name in required
        parsed["schemas"][schema_name] = schema

        # XXX does not follow schema for defaults:
        #   core settings::https_log_settings
        if schema_name in section_defaults and "default" not in schema:
            schema["default"] = section_defaults[schema_name]

        # XXX has no title:
        #   settings_gui::saml_login_settings::configure_authncc
        schema["title"] = schema.get("title", schema_name.replace("_", " ").title())

    return parsed


def parse_settings(raw, title=""):
    """Pass."""
    # XXX missing pretty_name:
    #   settings_gui
    #   settings_lifecycle
    title = raw["schema"].get("pretty_name", "") or title

    raw_config = raw["config"]
    raw_sections = raw["schema"]["items"]

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
