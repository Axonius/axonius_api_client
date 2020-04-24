# -*- coding: utf-8 -*-
"""Test suite."""
from axonius_api_client.api.parsers.tables import tab_map, tablize
from axonius_api_client.constants import KEY_MAP_SCHEMA


def test_tablize_footer_true():
    """Pass."""
    key = "badwolf1"
    key_value = "badwolf2"
    err = "badwolf3"

    exp = [err, "", key, "----------", key_value, "----------", key, "", err]

    value = [{key: key_value}]
    result = tablize(value=value, err=err, fmt="simple", footer=True)
    lines = result.splitlines()
    assert lines == exp


def test_tablize_footer_false():
    """Pass."""
    key = "badwolf1"
    key_value = "badwolf2"
    err = "badwolf3"

    exp = [err, "", key, "----------", key_value, "", err]

    value = [{key: key_value}]
    result = tablize(value=value, err=err, fmt="simple", footer=False)
    lines = result.splitlines()
    assert lines == exp


def test_tablize_err_false():
    """Pass."""
    key = "badwolf1"
    key_value = "badwolf2"

    exp = ["", "", key, "----------", key_value, "----------", key, ""]

    value = [{key: key_value}]
    result = tablize(value=value, err=None, fmt="simple", footer=True)
    lines = result.splitlines()
    assert lines == exp


def test_tab_map_orig_false():
    """Pass."""
    value = {"name": "schema_str", "type": "string", "required": False, "other": "bloop"}
    exp = {"Name": "schema_str", "Type": "string", "Required": False}
    result = tab_map(value=value, key_map=KEY_MAP_SCHEMA, orig=False)
    assert result == exp


def test_tab_map_orig_true():
    """Pass."""
    value = {"name": "schema_str", "type": "string", "required": False, "other": "bloop"}
    exp = {"Name": "schema_str", "Type": "string", "Required": False, "other": "bloop"}
    result = tab_map(value=value, key_map=KEY_MAP_SCHEMA, orig=True)
    assert result == exp


def test_tab_map_list():
    """Pass."""
    long_str = ("badwolf " * 30).split(" ")
    long_str_exp = "\n".join(long_str)
    value = {
        "name": long_str,
        "type": "string",
        "required": False,
    }
    exp = {
        "Name": long_str_exp,
        "Required": False,
        "Type": "string",
    }
    result = tab_map(value=value, key_map=KEY_MAP_SCHEMA)
    assert result == exp


def test_tab_map_long_str():
    """Pass."""
    long_str = "badwolf " * 30
    long_str_exp = (
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf\n"
        "badwolf badwolf badwolf"
    )
    value = {
        "title": long_str,
        "type": "string",
        "required": False,
    }
    exp = {
        "Title": long_str_exp,
        "Required": False,
        "Type": "string",
    }
    result = tab_map(value=value, key_map=KEY_MAP_SCHEMA)
    assert result == exp


def test_tab_map_list_other():
    """Pass."""
    value = {
        "name": "schema_str",
        "type": "string",
        "required": False,
        "other": ["bloop", "floop"],
    }
    exp = {
        "Name": "schema_str",
        "Type": "string",
        "Required": False,
        "other": "bloop\nfloop",
    }
    result = tab_map(value=value, key_map=KEY_MAP_SCHEMA, orig=True)
    assert result == exp
