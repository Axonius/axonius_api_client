# -*- coding: utf-8 -*-
"""Test suite."""
import pathlib

import click
import pytest

from axonius_api_client.cli.grp_adapters.grp_cnx import parsing
from axonius_api_client.constants.adapters import CNX_SANE_DEFAULTS


class TestParseConfig:
    def test_base(self):
        schemas = [
            {
                "name": "test_key1",
                "title": "Test Key1",
                "type": "string",
                "required": True,
            },
            {
                "name": "test_key2",
                "title": "Test Key2",
                "type": "bool",
                "required": False,
            },
        ]
        exp = {"test_key1": "xx", "test_key2": True}
        data = parsing.parse_config(
            schemas=schemas,
            adapter_name="foozball",
            config={"test_key1": "xx", "test_key2": "y"},
            error_as_exc=True,
        )
        assert data == exp

        with pytest.raises(parsing.SchemaError) as exc:
            parsing.parse_config(
                schemas=schemas,
                adapter_name="foozball",
                config={"test_key1": "xx", "test_key2": "y", "aaaa": "z"},
                error_as_exc=True,
            )
        assert "Unknown config keys supplied" in str(exc.value)

        parsing.parse_config(
            schemas=schemas,
            adapter_name="foozball",
            config={"test_key1": "xx", "test_key2": "y", "aaaa": "z"},
            ignore_unknowns=True,
            error_as_exc=True,
        )
        assert data == exp


class TestShows:
    def test_get_schemas_str(self):
        schemas = [
            {
                "name": "test_key1",
                "title": "Test Key1",
                "type": "string",
                "required": True,
            },
            {
                "name": "test_key2",
                "title": "Test Key2",
                "type": "string",
                "required": False,
            },
        ]
        objs = parsing.Schema.load_types(
            schemas=schemas, adapter_name="foozball", error_as_exc=True
        )
        data = parsing.get_schemas_str(schemas=objs)
        assert isinstance(data, str) and data
        assert "Required schemas: test_key1" in data
        assert "Optional schemas: test_key2" in data

    def test_get_defaults(self):
        schemas = [
            {
                "name": "test_key1",
                "title": "Test Key1",
                "type": "string",
                "required": True,
            },
            {
                "name": "test_key2",
                "title": "Test Key2",
                "type": "string",
                "required": False,
                "default": "xx",
            },
            {
                "name": "test_key3",
                "title": "Test Key3",
                "type": "bool",
                "required": False,
            },
        ]
        data = parsing.get_defaults(adapter_name="foozball", schemas=schemas)
        assert data["required"] == ["test_key1"]
        assert data["optional"] == ["test_key2", "test_key3"]
        assert data["sane_defaults"] == {"test_key3": False}
        assert data["schema_defaults"] == {"test_key2": "xx"}

    def test_get_defaults_str(self):
        schemas = [
            {
                "name": "test_key1",
                "title": "Test Key1",
                "type": "string",
                "required": True,
            },
            {
                "name": "test_key2",
                "title": "Test Key2",
                "type": "string",
                "required": False,
                "default": "xx",
            },
        ]
        data = parsing.get_defaults_str(adapter_name="foozball", schemas=schemas)
        assert isinstance(data, str)

    def test_handle_shows(self):
        schemas = [
            {
                "name": "test_key1",
                "title": "Test Key1",
                "type": "string",
                "required": True,
            },
            {
                "name": "test_key2",
                "title": "Test Key2",
                "type": "string",
                "required": False,
                "default": "xx",
            },
        ]
        data = parsing.get_show_data(adapter_name="foozball", schemas=schemas)
        assert data is None
        data = parsing.get_show_data(adapter_name="foozball", schemas=schemas, show_schemas=True)
        assert isinstance(data, str) and data
        data = parsing.get_show_data(adapter_name="foozball", schemas=schemas, show_defaults=True)
        assert isinstance(data, str) and data


class TestClickParams:
    def test_success(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "integer",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        param = parsing.SchemaClick(schema=obj)
        info_dict = param.to_info_dict()
        assert isinstance(info_dict, dict) and info_dict["schema"] == obj
        data = param.convert(value="2", param=None, ctx=None)
        assert data == 2

        with pytest.raises(click.BadParameter):
            param.convert(value="xxx", param=None, ctx=None)

    def test_fail(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "integer",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        param = parsing.SchemaClick(schema=obj)
        info_dict = param.to_info_dict()
        assert isinstance(info_dict, dict) and info_dict["schema"] == obj

        with pytest.raises(click.BadParameter):
            param.convert(value="xxx", param=None, ctx=None)


class TestSchemaString:
    def test_wrong_type(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "required": True,
        }
        with pytest.raises(ValueError) as exc:
            parsing.SchemaBool(schema=schema, adapter_name="foozball", error_as_exc=True)
        assert "type mismatch" in str(exc.value)

    def test_prompt_for_previous_false(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": None,
            "required": True,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", error_as_exc=True, prompt_for_previous=False
        )
        parsed = obj.parse(config={}, config_previous={"test_key": "xx"})
        assert parsed == "xx"

    def test_prompt_for_previous_true(self, monkeypatch):
        def mockprompt(*args, **kwargs):
            return "ZZZ"

        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": None,
            "required": True,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", error_as_exc=True, prompt_for_previous=True
        )
        monkeypatch.setattr(click, "prompt", mockprompt)
        parsed = obj.parse(config={}, config_previous={"test_key": "xx"})
        assert parsed == "ZZZ"

    def test_prompt_for_missing_required_false_required(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "required": True,
        }
        obj = parsing.Schema.load_type(
            schema=schema,
            adapter_name="foozball",
            error_as_exc=True,
            prompt_for_missing_required=False,
        )
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={})
        assert "Must supply value!" in str(exc.value)

    def test_prompt_for_missing_required_true(self, monkeypatch):
        def mockprompt(*args, **kwargs):
            return "ZZZ"

        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": None,
            "required": True,
        }
        obj = parsing.Schema.load_type(
            schema=schema,
            adapter_name="foozball",
            error_as_exc=True,
            prompt_for_missing_required=True,
        )
        monkeypatch.setattr(click, "prompt", mockprompt)
        parsed = obj.parse(config={})
        assert parsed == "ZZZ"

    def test_prompt_for_optional_true(self, monkeypatch):
        def mockprompt(*args, **kwargs):
            return "ZZZ"

        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": "abc",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", error_as_exc=True, prompt_for_optional=True
        )
        monkeypatch.setattr(click, "prompt", mockprompt)
        parsed = obj.parse(config={})
        assert parsed == "ZZZ"

    def test_prompt_for_optional_false(self, monkeypatch):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": "abc",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", error_as_exc=True, prompt_for_optional=False
        )
        parsed = obj.parse(config={})
        assert parsed == "abc"

    def test_prompt_for_default_true(self, monkeypatch):
        def mockprompt(*args, **kwargs):
            return "ZZZ"

        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": "abc",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", error_as_exc=True, prompt_for_default=True
        )
        monkeypatch.setattr(click, "prompt", mockprompt)
        parsed = obj.parse(config={})
        assert parsed == "ZZZ"

    def test_prompt_for_default_false(self, monkeypatch):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": "abc",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", error_as_exc=True, prompt_for_default=False
        )
        parsed = obj.parse(config={})
        assert parsed == "abc"

    def test_prompt_default_from_schema_none(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": None,
            "required": False,
        }
        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)
        assert obj.has_default is True
        assert obj.prompt_default == obj.NULL[0]
        parsed = obj.parse(config={"test_key": "None"})
        assert parsed == obj.NULL_PARSED

    def test_prompt_default_from_schema_str(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": "aaaa",
            "required": False,
        }
        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)
        assert obj.has_default is True
        assert obj.prompt_default == schema["default"]

    def test_prompt_default_from_sane_default(self, monkeypatch):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "required": False,
        }
        with monkeypatch.context() as m:
            m.setitem(CNX_SANE_DEFAULTS, "foozball", {"test_key": None})
            obj = parsing.Schema.load_type(
                schema=schema, adapter_name="foozball", error_as_exc=True
            )
            assert obj.has_sane_default is True
            assert obj.prompt_default == obj.NULL[0]
            obj = parsing.Schema.load_type(
                schema=schema, adapter_name="foozball", error_as_exc=True, use_sane_defaults=False
            )
            assert obj.has_sane_default is False

    def test_use_default_err_required(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "enum": ["a", "b", "c"],
            "required": True,
        }
        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "USE_DEFAULT"})
        assert f"Schema has {obj.default_source} - can not {obj.USE_DEFAULT}" in str(exc.value)

    def test_unchanged(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "format": "password",
        }
        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)
        assert obj.hide_value is True
        assert obj.hide(value="ZZZ") == "3_CHARACTERS_HIDDEN"
        assert "Input will be hidden" in obj.prompt_text
        parsed = obj.parse(config={"test_key": "['unchanged']"})
        assert parsed == ["unchanged"]

        parsed = obj.parse(config={"test_key": ["unchanged"]})
        assert parsed == ["unchanged"]

        parsed = obj.parse(config={"test_key": '["unchanged"]'})
        assert parsed == ["unchanged"]

    def test_use_default_from_schema(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "default": "xx",
        }
        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)

        parsed = obj.parse(config={"test_key": "USE_DEFAULT"})
        assert parsed == "xx"

    def test_use_default_from_sane(self, monkeypatch):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
        }
        with monkeypatch.context() as m:
            m.setitem(CNX_SANE_DEFAULTS, "foozball", {"test_key": "XX"})
            obj = parsing.Schema.load_type(
                schema=schema, adapter_name="foozball", error_as_exc=True
            )

            parsed = obj.parse(config={"test_key": "USE_DEFAULT"})
            assert parsed == "XX"

    def test_email(self):
        schema = {
            "format": "email",
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "required": False,
        }

        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)
        assert isinstance(obj, parsing.SchemaString)
        assert isinstance(obj.click_type, click.types.ParamType)
        assert obj.click_type.to_info_dict()["schema"] == obj
        data = obj.parse_value(value="abc@abc.com")
        assert data == "abc@abc.com"
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse_value(value="xxx")
        assert "Value must be a valid email" in str(exc.value)

    def test_attrs(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "string",
            "enum": ["a", "b", "c"],
            "required": True,
        }
        objs = parsing.Schema.load_types(
            schemas=[schema], adapter_name="foozball", error_as_exc=True
        )
        assert isinstance(objs, list) and len(objs) == 1
        assert isinstance(objs[0], parsing.SchemaString)

        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)
        assert isinstance(obj, parsing.SchemaString)
        assert isinstance(obj.click_type, click.types.ParamType)
        assert obj.click_type.to_info_dict()["schema"] == obj

        assert schema["name"] in str(obj)
        assert schema["name"] in repr(obj)
        assert schema["name"] == obj.name
        assert schema["type"] == obj.for_type()
        assert schema["type"] == obj.type
        assert schema["enum"] == obj.enum
        assert obj.hide_value is False
        assert obj.default is None
        assert obj.has_default is False
        assert obj.has_sane_default is False
        assert obj.sane_default is None
        assert isinstance(obj.prompt_text_pre, list)
        assert "Input fill be hidden" not in obj.prompt_text
        assert "Value must be one of" in obj.prompt_text
        assert obj.prompt_default is None
        assert isinstance(obj.prompt_args, dict) and obj.prompt_args

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse_pre(value="None")
        assert "can not use" in str(exc.value)

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": obj.NULL[0]})
        assert "Value is required, can not use empty sentinel" in str(exc.value)

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": ""})
        assert "Value is required, must be a non-empty string" in str(exc.value)

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "d"})
        assert "Value must be one of" in str(exc.value)

        parsed = obj.parse(config={"test_key": "a"})
        assert parsed == "a"

        strs = obj.to_strs()
        assert isinstance(strs, list) and strs
        assert all([isinstance(x, str) for x in strs])

        assert schema["name"] in obj.info("test")
        assert schema["name"] in obj.debug("test")
        assert schema["name"] in obj.warn("test")
        assert schema["name"] in obj.error("test", abort=False)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.error("test")
        assert "Error in Schema 'test_key': test" in str(exc.value)
        obj.in_prompt_mode = True
        with pytest.raises(parsing.PromptError) as exc:
            obj.error("test")
        obj.in_prompt_mode = False
        assert "While in prompt mode for" in str(exc.value)


class TestSchemaArray:
    def test_check_enum_success(self):
        enum = [
            {"title": "Daily Usage", "name": "daily"},
            {"title": "Weekly Usage", "name": "weekly"},
            {"title": "Monthly Usage", "name": "monthly"},
        ]
        schema = {
            "name": "schedule",
            "title": "Schedule to run",
            "type": "array",
            "items": {"enum": enum, "type": "string"},
            "default": [],
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaArray)
        assert isinstance(obj.enum_details, str) and obj.enum_details
        assert obj.enum == [x["name"] for x in enum]
        assert obj.default == schema["default"]
        assert "Enter values seperated by" in obj.prompt_text
        assert "Value must be one" in obj.prompt_text
        parsed = obj.check_enum(value=["daily"])
        assert parsed == ["daily"]
        parsed = obj.parse(config={"schedule": "  daily  ,   monthly,,"})
        assert parsed == ["daily", "monthly"]

    def test_check_enum_failure(self):
        enum = [
            {"title": "Daily Usage", "name": "daily"},
            {"title": "Weekly Usage", "name": "weekly"},
            {"title": "Monthly Usage", "name": "monthly"},
        ]
        schema = {
            "name": "schedule",
            "title": "Schedule to run",
            "type": "array",
            "items": {"enum": enum, "type": "string"},
            "default": [],
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaArray)

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"schedule": "monthly, zzzzzzzzzzzzz"})
        assert "values must be one of" in str(exc.value)

    def test_check_empty_required(self):
        enum = [
            {"title": "Daily Usage", "name": "daily"},
            {"title": "Weekly Usage", "name": "weekly"},
            {"title": "Monthly Usage", "name": "monthly"},
        ]
        schema = {
            "name": "schedule",
            "title": "Schedule to run",
            "type": "array",
            "items": {"enum": enum, "type": "string"},
            "required": True,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"schedule": " , "})
        assert "Empty value" in str(exc.value)
        assert "after splitting" in str(exc.value)


class TestSchemaFile:
    def test_parse_valid_file(self, tmp_path):
        path = tmp_path / "test.txt"
        path.touch()

        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        parsed = obj.parse(config={"test_key": f"{path}"})
        assert parsed == path
        assert "Can start value with" in obj.prompt_text

    def test_parse_file_object_success(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        parsed = obj.parse(config={"test_key": '{"filename": "xx", "uuid": "xx"}'})
        assert parsed == {"filename": "xx", "uuid": "xx"}

    def test_parse_file_object_failure_bad_json(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": '{"filename": , "uuid": }'})
        assert "Invalid JSON in file dictionary" in str(exc.value)

    def test_check_file_object_success(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        parsed = obj.parse(config={"test_key": {"filename": "bad", "uuid": "dee", "ignore": "me"}})
        assert parsed == {"filename": "bad", "uuid": "dee"}

    def test_check_file_object_failure(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": {"bad": "dee"}})
        assert "Required file object key" in str(exc.value)

    def test_check_file_object_failure_bad_type(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.check_file_object(value=[])
        assert "must be a dictionary" in str(exc.value)

    def test_parse_bad_type(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": 1111})
        assert "Value must be a string or a " in str(exc.value)

    def test_parse_valid_content(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        parsed = obj.parse(config={"test_key": obj.CONTENT + r"blah\nblah\n"})
        assert isinstance(parsed, pathlib.Path)
        assert parsed.is_file()

    def test_parse_invalid_file(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "file",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaFile)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "zzzzzzzzzzzzz"})
        assert "No file found at" in str(exc.value)


class TestSchemaInteger:
    def test_parse_success(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "integer",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaInteger)
        parsed = obj.parse(config={"test_key": "44"})
        assert parsed == 44

    def test_enum(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "integer",
            "enum": [1, 2, 3, 4],
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaInteger)
        parsed = obj.parse(config={"test_key": "4"})
        assert parsed == 4
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "5"})
        assert "Supplied value '5' is not one of" in str(exc.value)

    def test_max_min(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "integer",
            "max": 5,
            "min": 1,
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaInteger)
        for i in range(1, 5):
            parsed = obj.parse(config={"test_key": f"{i}"})
            assert parsed == i

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "6"})
        assert "is greater than max value" in str(exc.value)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "0"})
        assert "is less than min value of" in str(exc.value)

    def test_parse_fail(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "integer",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaInteger)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "zz"})
        assert "type str is not an integer." in str(exc.value)


class TestSchemaNumber:
    def test_parse_success(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "number",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaInteger)
        parsed = obj.parse(config={"test_key": "44"})
        assert parsed == 44

    def test_parse_fail(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "number",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaInteger)
        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "zz"})
        assert "type str is not an integer." in str(exc.value)


class TestSchemaBool:
    def test_sane_default(self):
        schema = {
            "name": "verify_ssl",
            "title": "Verify SSL",
            "type": "bool",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaBool)
        assert obj.has_sane_default is True
        assert obj.sane_default is False

    def test_sane_default_yes(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "bool",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=True, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaBool)
        assert obj.has_sane_default is True
        assert obj.sane_default is False

    def test_sane_default_no(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "bool",
            "required": False,
        }
        obj = parsing.Schema.load_type(
            schema=schema, adapter_name="foozball", use_sane_defaults=False, error_as_exc=True
        )
        assert isinstance(obj, parsing.SchemaBool)
        assert obj.has_sane_default is False
        assert obj.sane_default is None

    def test_success(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "bool",
            "required": False,
        }
        objs = parsing.Schema.load_types(
            schemas=[schema], adapter_name="foozball", error_as_exc=True
        )
        assert isinstance(objs, list) and len(objs) == 1
        assert isinstance(objs[0], parsing.SchemaBool)

        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)
        assert isinstance(obj, parsing.SchemaBool)
        assert isinstance(obj.click_type, click.types.ParamType)
        assert obj.click_type.to_info_dict()["schema"] == obj
        parsed = obj.parse(config={"test_key": "y"})
        assert parsed is True

    def test_fail(self):
        schema = {
            "name": "test_key",
            "title": "Test Key",
            "type": "bool",
            "required": False,
        }
        objs = parsing.Schema.load_types(
            schemas=[schema], adapter_name="foozball", error_as_exc=True
        )
        assert isinstance(objs, list) and len(objs) == 1
        assert isinstance(objs[0], parsing.SchemaBool)

        obj = parsing.Schema.load_type(schema=schema, adapter_name="foozball", error_as_exc=True)
        assert isinstance(obj, parsing.SchemaBool)
        assert isinstance(obj.click_type, click.types.ParamType)
        assert obj.click_type.to_info_dict()["schema"] == obj

        with pytest.raises(parsing.SchemaError) as exc:
            obj.parse(config={"test_key": "zz"})
        assert "For True:" in str(exc.value)
