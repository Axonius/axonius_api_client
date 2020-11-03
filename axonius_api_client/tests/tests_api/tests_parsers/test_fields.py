# -*- coding: utf-8 -*-
"""Test suite."""
from axonius_api_client.parsers.fields import schema_custom


def test_schema_custom():
    schema = schema_custom("badwolf")
    exp = {
        "adapter_name_raw": "custom",
        "adapter_name": "custom",
        "adapter_title": "Custom",
        "adapter_prefix": "cu",
        "column_name": "custom:badwolf",
        "column_title": "Custom: Badwolf",
        "sub_fields": [],
        "is_complex": False,
        "is_list": False,
        "is_root": True,
        "parent": "root",
        "name": "badwolf",
        "name_base": "badwolf",
        "name_qual": "badwolf",
        "title": "Badwolf",
        "type": "string",
        "type_norm": "string",
        "selectable": False,
        "is_agg": False,
        "expr_field_type": "agg",
        "is_all": False,
        "is_details": False,
    }
    assert schema == exp
