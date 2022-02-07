# -*- coding: utf-8 -*-
"""Test suite."""
import copy

import pytest

from axonius_api_client.constants.api import SETTING_UNCHANGED
from axonius_api_client.exceptions import (
    ApiError,
    ConfigInvalidValue,
    ConfigRequired,
    ConfigUnchanged,
    ConfigUnknown,
)
from axonius_api_client.parsers.config import (
    config_check,
    config_check_array,
    config_check_bool,
    config_check_file,
    config_check_int,
    config_check_str,
    config_default,
    config_empty,
    config_required,
    config_unchanged,
    config_unknown,
    is_uploaded_file,
    parse_schema,
)

from ...meta import (
    SCHEMA_ARRAY,
    SCHEMA_BOOL,
    SCHEMA_FILE,
    SCHEMA_INT,
    SCHEMA_NUM,
    SCHEMA_STR,
    SCHEMA_STR_ENUM,
    SCHEMA_STR_PASSWORD,
    SCHEMA_UNKNOWN,
    SCHEMAS,
    SCHEMAS_DICT,
)


def test_config_check_str():
    value = "test"
    result = config_check_str(value=value, schema=SCHEMA_STR, source="badwolf")
    assert result == value

    result = config_check(value=value, schema=SCHEMA_STR, source="badwolf")
    assert result == value


def test_config_check_str_bad():
    value = {"11111": "x"}
    with pytest.raises(ConfigInvalidValue):
        config_check_str(value=value, schema=SCHEMA_STR, source="badwolf")

    with pytest.raises(ConfigInvalidValue):
        config_check(value=value, schema=SCHEMA_STR, source="badwolf")


@pytest.mark.parametrize(
    "value",
    [
        SETTING_UNCHANGED,
        SETTING_UNCHANGED[0],
        str(SETTING_UNCHANGED),
        str(SETTING_UNCHANGED[0]),
    ],
)
def test_config_check_str_password_unchanged(value):
    result = config_check_str(value=value, schema=SCHEMA_STR_PASSWORD, source="badwolf")
    assert result == SETTING_UNCHANGED

    result = config_check(value=value, schema=SCHEMA_STR_PASSWORD, source="badwolf")
    assert result == SETTING_UNCHANGED


def test_config_check_str_password():
    value = "badwolf"
    result = config_check_str(value=value, schema=SCHEMA_STR_PASSWORD, source="badwolf")
    assert result == value

    result = config_check(value=value, schema=SCHEMA_STR_PASSWORD, source="badwolf")
    assert result == value


def test_config_check_str_enum():
    value = "badwolf"
    result = config_check_str(value=value, schema=SCHEMA_STR_ENUM, source="badwolf")
    assert result == value

    result = config_check(value=value, schema=SCHEMA_STR_ENUM, source="badwolf")
    assert result == value


def test_config_check_str_enum_bad():
    value = "xxxx"
    with pytest.raises(ConfigInvalidValue):
        config_check_str(value=value, schema=SCHEMA_STR_ENUM, source="badwolf")

    with pytest.raises(ConfigInvalidValue):
        config_check(value=value, schema=SCHEMA_STR_ENUM, source="badwolf")


@pytest.mark.parametrize("schema", [SCHEMA_INT, SCHEMA_NUM])
def test_config_check_int(schema):
    value = 111
    result = config_check_int(value=value, schema=schema, source="badwolf")
    assert result == value

    result = config_check(value=value, schema=schema, source="badwolf")
    assert result == value


@pytest.mark.parametrize("schema", [SCHEMA_INT, SCHEMA_NUM])
def test_config_check_int_str(schema):
    value = "111"
    exp = 111
    result = config_check_int(value=value, schema=schema, source="badwolf")
    assert result == exp

    result = config_check(value=value, schema=schema, source="badwolf")
    assert result == exp


@pytest.mark.parametrize("schema", [SCHEMA_INT, SCHEMA_NUM])
def test_config_check_int_bad(schema):
    value = "badwolf"
    with pytest.raises(ConfigInvalidValue):
        config_check_int(value=value, schema=schema, source="badwolf")
    with pytest.raises(ConfigInvalidValue):
        config_check(value=value, schema=schema, source="badwolf")


def test_config_check_bool_bad():
    value = "badwolf"
    with pytest.raises(ConfigInvalidValue):
        config_check_bool(value=value, schema=SCHEMA_BOOL, source="badwolf")

    with pytest.raises(ConfigInvalidValue):
        config_check(value=value, schema=SCHEMA_BOOL, source="badwolf")


def test_config_check_bool_yes():
    value = "yes"
    exp = True
    result = config_check_bool(value=value, schema=SCHEMA_BOOL, source="badwolf")
    assert result == exp

    result = config_check(value=value, schema=SCHEMA_BOOL, source="badwolf")
    assert result == exp


def test_config_check_bool_no():
    value = "no"
    exp = False
    result = config_check_bool(value=value, schema=SCHEMA_BOOL, source="badwolf")
    assert result == exp

    result = config_check(value=value, schema=SCHEMA_BOOL, source="badwolf")
    assert result == exp


def test_config_check_array_list():
    value = ["badwolf1", "badwolf2"]
    result = config_check_array(value=value, schema=SCHEMA_ARRAY, source="badwolf")
    assert result == value

    result = config_check(value=value, schema=SCHEMA_ARRAY, source="badwolf")
    assert result == value


def test_config_check_array_str():
    value = "badwolf1, badwolf2"
    exp = ["badwolf1", "badwolf2"]
    result = config_check_array(value=value, schema=SCHEMA_ARRAY, source="badwolf")
    assert result == exp

    result = config_check(value=value, schema=SCHEMA_ARRAY, source="badwolf")
    assert result == exp


@pytest.mark.parametrize("value", [1111, [111]])
def test_config_check_array_bad(value):
    with pytest.raises(ConfigInvalidValue):
        config_check_array(value=value, schema=SCHEMA_ARRAY, source="badwolf")
    with pytest.raises(ConfigInvalidValue):
        config_check(value=value, schema=SCHEMA_ARRAY, source="badwolf")


def test_config_check_file_uploaded():
    value = {"uuid": "x", "filename": "x"}
    result = config_check_file(value=value, schema=SCHEMA_FILE, source="badwolf")
    assert value == result

    result = config_check(value=value, schema=SCHEMA_FILE, source="badwolf")
    assert value == result


def test_config_check_file_callback():
    def mock_callback(value, schema, callbacks, source):
        return {"uuid": "x", "filename": "x"}

    value = "badwolf"
    exp = {"uuid": "x", "filename": "x"}
    callbacks = {"cb_file": mock_callback}
    result = config_check_file(
        value=value, schema=SCHEMA_FILE, source="badwolf", callbacks=callbacks
    )
    assert result == exp

    result = config_check(value=value, schema=SCHEMA_FILE, source="badwolf", callbacks=callbacks)
    assert result == exp


def test_config_check_file_unsupported():
    value = "x"
    with pytest.raises(ApiError):
        config_check_file(value=value, schema=SCHEMA_FILE, source="badwolf")

    with pytest.raises(ApiError):
        config_check(value=value, schema=SCHEMA_FILE, source="badwolf")


def test_config_check_unknown_schema():
    value = "badwolf"
    with pytest.raises(ApiError):
        config_check(value=value, schema=SCHEMA_UNKNOWN, source="badwolf")


@pytest.mark.parametrize("schema", SCHEMAS)
def test_config_check_none_ok(schema):
    value = None
    result = config_check(value=value, schema=schema, none_ok=True, source="badwolf")
    assert result == value


@pytest.mark.parametrize("schema", SCHEMAS)
def test_config_check_none_bad(schema):
    value = None
    with pytest.raises(ConfigInvalidValue):
        config_check(value=value, schema=schema, none_ok=False, source="badwolf")


def test_parse_schema_req_true():
    schema = {"items": [{"name": "x"}], "required": ["x"]}
    exp = {"x": {"name": "x", "required": True, "hide_value": False}}
    result = parse_schema(raw=schema)
    assert result == exp


def test_parse_schema_req_false():
    schema = {"items": [{"name": "x"}], "required": []}
    exp = {"x": {"name": "x", "required": False, "hide_value": False}}
    result = parse_schema(raw=schema)
    assert result == exp


def test_is_uploaded_file_true():
    value = {"uuid": "x", "filename": "x"}
    exp = True, value
    result = is_uploaded_file(value=value)
    assert result == exp


def test_is_uploaded_file_true_json():
    value = '{"uuid": "x", "filename": "x"}'
    exp = True, {"uuid": "x", "filename": "x"}
    result = is_uploaded_file(value=value)
    assert result == exp


def test_is_uploaded_file_false_json():
    value = '{"uu": "x", "filename": "x"}'
    exp = False, value
    result = is_uploaded_file(value=value)
    assert result == exp


@pytest.mark.parametrize(
    "value",
    [
        "x",
        {},
        {"uuid": "x"},
        {"uuid": ""},
        {"filename": "x"},
        {"filename": ""},
        {"uuid": "", "filename": ""},
        {"uuid": [""], "filename": [""]},
    ],
)
def test_is_uploaded_file_false(value):
    exp = False, value
    result = is_uploaded_file(value=value)
    assert result == exp


def test_config_empty_ok():
    config_empty(schemas=SCHEMAS_DICT, new_config={"badwolf": "badwolf"}, source="badwolf")


def test_config_empty_bad():
    with pytest.raises(ConfigRequired):
        config_empty(schemas=SCHEMAS_DICT, new_config={}, source="badwolf")


@pytest.mark.parametrize(
    "value",
    [{}, {"x": "x"}, {SCHEMA_STR["name"]: "vvv"}],
)
def test_config_required_ok(value):
    schemas = copy.deepcopy(SCHEMAS_DICT)
    for name, schema in schemas.items():
        schema["required"] = False
    config_required(schemas=schemas, new_config=value, source="badwolf")


def test_config_required_bad():
    schemas = copy.deepcopy(SCHEMAS_DICT)
    for name, schema in schemas.items():
        schema["required"] = True
    with pytest.raises(ConfigRequired):
        config_required(schemas=schemas, new_config={}, source="badwolf")


def test_config_required_ignored():
    schemas = copy.deepcopy(SCHEMAS_DICT)
    for name, schema in schemas.items():
        schema["required"] = True
    ignores = list(schemas)
    config_required(schemas=schemas, new_config={}, source="badwolf", ignores=ignores)


@pytest.mark.parametrize(
    "value",
    [{}, {"x": "x"}, {SCHEMA_STR["name"]: "moo"}, {SCHEMA_STR["name"]: "moo", "x": "x"}],
)
def test_config_default(value):
    schemas = copy.deepcopy(SCHEMAS_DICT)
    exp = {}
    for name, schema in schemas.items():
        schema["default"] = "badwolf"
        exp[name] = "badwolf"
    exp.update(value)
    result = config_default(schemas=schemas, new_config=copy.deepcopy(value), source="badwolf")
    assert result == exp


def test_config_changed_ok():
    config_unchanged(
        schemas=SCHEMAS_DICT,
        old_config={"x": "x"},
        new_config={"x": "y"},
        source="badwolf",
    )


@pytest.mark.parametrize(
    "value",
    [{}, {"x": "x"}],
)
def test_config_changed_bad(value):
    with pytest.raises(ConfigUnchanged):
        config_unchanged(
            schemas=SCHEMAS_DICT,
            old_config={"x": "x"},
            new_config=value,
            source="badwolf",
        )


def test_config_unknown_ok():
    schema_name = SCHEMA_STR["name"]
    config = {schema_name: "badwolf"}
    config_unknown(schemas=SCHEMAS_DICT, new_config=config, source="badwolf")


def test_config_unknown_bad():
    config = {"badwolf": "badwolf"}
    with pytest.raises(ConfigUnknown):
        config_unknown(schemas=SCHEMAS_DICT, new_config=config, source="badwolf")
