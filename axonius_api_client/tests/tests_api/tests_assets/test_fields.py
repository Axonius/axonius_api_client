# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy

import pytest
from axonius_api_client.constants import AGG_ADAPTER_ALTS, AGG_ADAPTER_NAME
from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import FIELD_FORMATS, SCHEMA_FIELD_FORMATS, SCHEMA_TYPES
from ...utils import get_schemas


class FieldsPrivate:
    def test_private_get(self, apiobj):
        fields = apiobj.fields._get()
        self.val_raw_fields(fields=fields)

    def val_raw_fields(self, fields):
        fields = copy.deepcopy(fields)
        assert isinstance(fields, dict)

        schema = fields.pop("schema")
        assert isinstance(schema, dict)

        generic = fields.pop("generic")
        assert isinstance(generic, list)
        self.val_raw_adapter_fields(adapter="generic", adapter_fields=generic)

        generic_schema = schema.pop("generic")
        assert isinstance(generic_schema, dict)
        self.val_raw_schema(adapter="generic", schema=generic_schema)

        specific = fields.pop("specific")
        assert isinstance(specific, dict)

        specific_schema = schema.pop("specific")
        assert isinstance(specific_schema, dict)

        for adapter, adapter_fields in specific.items():
            self.val_raw_adapter_fields(adapter=adapter, adapter_fields=adapter_fields)
            adapter_schema = specific_schema.pop(adapter)
            self.val_raw_schema(adapter=adapter, schema=adapter_schema)

        assert not fields
        assert not schema

    def val_raw_schema(self, adapter, schema):
        assert isinstance(schema, dict)

        items = schema.pop("items")
        assert isinstance(items, list)

        required = schema.pop("required")
        assert isinstance(required, list)

        stype = schema.pop("type")
        assert stype == "array"

        assert not schema, list(schema)

        for req in required:
            assert isinstance(req, str)

        for item in items:
            assert item
            self.val_raw_items(adapter=adapter, items=item)

    def val_raw_adapter_fields(self, adapter, adapter_fields):
        assert isinstance(adapter_fields, list)

        for field in adapter_fields:
            assert isinstance(field, dict)

            name = field.pop("name")
            assert isinstance(name, str) and name

            title = field.pop("title")
            assert isinstance(title, str) and title

            ftype = field.pop("type")
            assert isinstance(ftype, str) and ftype
            assert ftype in SCHEMA_TYPES

            description = field.pop("description", "")
            assert isinstance(description, str)

            sort = field.pop("sort", False)
            assert isinstance(sort, bool)

            unique = field.pop("unique", False)
            assert isinstance(unique, bool)

            branched = field.pop("branched", False)
            assert isinstance(branched, bool)

            dynamic = field.pop("dynamic", False)
            assert isinstance(dynamic, bool)

            fformat = field.pop("format", "")
            assert isinstance(fformat, str)
            assert fformat in FIELD_FORMATS or fformat == ""

            enums = field.pop("enum", [])
            assert isinstance(enums, list)
            for enum in enums:
                assert isinstance(enum, str) or isinstance(enum, int)

            items = field.pop("items", {})
            assert isinstance(items, dict)

            self.val_raw_items(adapter=f"{adapter}:{name}", items=items)

            assert not field, list(field)

    def val_raw_items(self, adapter, items):
        assert isinstance(items, dict)

        if items:
            ftype = items.pop("type")
            assert isinstance(ftype, str)
            assert ftype in SCHEMA_TYPES

            description = items.pop("description", "")
            assert isinstance(description, str)

            title = items.pop("title", "")
            assert isinstance(title, str)

            name = items.pop("name", "")
            assert isinstance(name, str)

            sort = items.pop("sort", False)
            assert isinstance(sort, bool)

            unique = items.pop("unique", False)
            assert isinstance(unique, bool)

            branched = items.pop("branched", False)
            assert isinstance(branched, bool)

            dynamic = items.pop("dynamic", False)
            assert isinstance(dynamic, bool)

            hidden = items.pop("hidden", False)
            assert isinstance(hidden, bool)

            iformat = items.pop("format", "")
            assert isinstance(iformat, str)
            assert iformat in SCHEMA_FIELD_FORMATS or iformat == ""

            val_source(obj=items)

            enums = items.pop("enum", [])
            assert isinstance(enums, list)

            for enum in enums:
                assert isinstance(enum, str) or isinstance(enum, int)

            sub_items = items.pop("items", [])
            assert isinstance(sub_items, list) or isinstance(sub_items, dict)
            assert not items, list(items)

            if isinstance(sub_items, dict):
                self.val_raw_items(adapter=adapter, items=sub_items)
            else:
                for sub_item in sub_items:
                    self.val_raw_items(adapter=adapter, items=sub_item)

    def test_private_prettify_schemas(self, apiobj):
        schemas = get_schemas(apiobj=apiobj)
        pretty = apiobj.fields._prettify_schemas(schemas=schemas)
        assert isinstance(pretty, list)
        for p in pretty:
            assert isinstance(p, str)
            assert "->" in p


class FieldsPublic:
    def test_get(self, apiobj):
        fields = apiobj.fields.get()
        self.val_parsed_fields(fields=fields)

    def val_parsed_fields(self, fields):
        fields = copy.deepcopy(fields)
        assert isinstance(fields, dict)

        for adapter, schemas in fields.items():
            assert not adapter.endswith("_adapter")
            assert isinstance(schemas, list)

            for schema in schemas:
                self.val_parsed_schema(schema=schema, adapter=adapter)

    def val_parsed_schema(self, schema, adapter):
        schema = copy.deepcopy(schema)
        assert isinstance(schema, dict)

        name = schema.pop("name")
        assert isinstance(name, str) and name

        ftype = schema.pop("type")
        assert isinstance(ftype, str) and ftype
        assert ftype in SCHEMA_TYPES

        fformat = schema.pop("format", "")
        assert isinstance(fformat, str)
        assert fformat in FIELD_FORMATS or fformat == ""

        adapter_name = schema.pop("adapter_name")
        assert isinstance(adapter_name, str) and adapter_name

        adapter_name_raw = schema.pop("adapter_name_raw")
        assert isinstance(adapter_name_raw, str) and adapter_name_raw

        adapter_prefix = schema.pop("adapter_prefix")
        assert isinstance(adapter_prefix, str) and adapter_prefix

        adapter_title = schema.pop("adapter_title")
        assert isinstance(adapter_title, str) and adapter_title

        column_name = schema.pop("column_name")
        assert isinstance(column_name, str) and column_name

        column_title = schema.pop("column_title")
        assert isinstance(column_title, str) and column_title

        name_base = schema.pop("name_base")
        assert isinstance(name_base, str) and name_base

        name_qual = schema.pop("name_qual")
        assert isinstance(name_qual, str) and name_qual

        title = schema.pop("title")
        assert isinstance(title, str) and title

        type_norm = schema.pop("type_norm")
        assert isinstance(type_norm, str) and type_norm

        parent = schema.pop("parent")
        assert isinstance(parent, str) and parent

        is_root = schema.pop("is_root")
        assert isinstance(is_root, bool)

        is_list = schema.pop("is_list")
        assert isinstance(is_list, bool)

        selectable = schema.pop("selectable", False)
        assert isinstance(selectable, bool)

        description = schema.pop("description", "")
        assert isinstance(description, str)

        sort = schema.pop("sort", False)
        assert isinstance(sort, bool)

        unique = schema.pop("unique", False)
        assert isinstance(unique, bool)

        branched = schema.pop("branched", False)
        assert isinstance(branched, bool)

        dynamic = schema.pop("dynamic", False)
        assert isinstance(dynamic, bool)

        is_complex = schema.pop("is_complex")
        assert isinstance(is_complex, bool)

        enums = schema.pop("enum", [])
        assert isinstance(enums, list)

        is_agg = schema.pop("is_agg")
        assert isinstance(is_agg, bool)

        expr_field_type = schema.pop("expr_field_type")
        assert isinstance(expr_field_type, str)

        for enum in enums:
            assert isinstance(enum, str) or isinstance(enum, int)

        sub_fields = schema.pop("sub_fields", [])
        assert isinstance(sub_fields, list)

        items = schema.pop("items", {})
        assert isinstance(items, dict)

        if is_complex:
            if name != "all":
                assert sub_fields

            for sub_field in sub_fields:
                self.val_parsed_schema(adapter=f"{adapter}:{name}", schema=sub_field)
        else:
            dynamic = items.pop("dynamic", False)
            assert isinstance(dynamic, bool)

            iformat = items.pop("format", "")
            assert isinstance(iformat, str)
            assert iformat in SCHEMA_FIELD_FORMATS or iformat == ""

            itype = items.pop("type", "")
            assert isinstance(itype, str)
            assert itype in SCHEMA_TYPES or itype == ""

            val_source(obj=items)

            enums = items.pop("enum", [])
            assert isinstance(enums, list)

            for enum in enums:
                assert isinstance(enum, str) or isinstance(enum, int)

            assert not items

        assert not schema, list(schema)

    def test_get_adapter_name(self, apiobj):
        search = AGG_ADAPTER_ALTS[0]
        exp = AGG_ADAPTER_NAME
        adapter = apiobj.fields.get_adapter_name(value=search)
        assert adapter == exp

    def test_get_adapter_name_error(self, apiobj):
        search = "badwolf"
        with pytest.raises(NotFoundError):
            apiobj.fields.get_adapter_name(value=search)

    def test_get_adapter_names_single(self, apiobj):
        search = AGG_ADAPTER_ALTS[0]
        exp = [AGG_ADAPTER_NAME]
        adapters = apiobj.fields.get_adapter_names(value=search)
        assert adapters == exp

    def test_get_adapter_names_multi(self, apiobj):
        search = "a"
        adapters = apiobj.fields.get_adapter_names(value=search)
        assert AGG_ADAPTER_NAME in adapters
        assert len(adapters) > 1

    def test_get_adapter_names_error(self, apiobj):
        search = "badwolf"
        with pytest.raises(NotFoundError):
            apiobj.fields.get_adapter_names(value=search)

    def test_get_field_schema(self, apiobj):
        search = "last_seen"
        schemas = get_schemas(apiobj=apiobj)
        exp = [x for x in schemas if x["name_base"] == search][0]
        result = apiobj.fields.get_field_schema(value=search, schemas=schemas)
        assert exp == result

    def test_get_field_names_re(self, apiobj):
        search = ["seen"]
        result = apiobj.fields.get_field_names_re(value=search)
        assert "specific_data.data.last_seen" in result

    def test_get_field_names_eq(self, apiobj):
        search = ["specific_data.data.id", "last_seen"]
        exp = []
        schemas = get_schemas(apiobj=apiobj)
        for i in search:
            exp += [
                x["name_qual"]
                for x in schemas
                if x["name_base"] == i or x["name_qual"] == i
            ]
        result = apiobj.fields.get_field_names_eq(value=search)
        assert exp == result

    def test_get_field_schemas(self, apiobj):
        # schemas = get_schemas(apiobj=apiobj)
        search = "l"
        result = [
            x["name_qual"]
            for x in apiobj.fields.get_field_schemas(
                value=search, schemas=get_schemas(apiobj=apiobj)
            )
        ]
        assert len(result) >= 1

    def test_get_field_schema_error(self, apiobj):
        search = "badwolf"
        schemas = get_schemas(apiobj=apiobj)
        with pytest.raises(NotFoundError):
            apiobj.fields.get_field_schema(value=search, schemas=schemas)

    @pytest.mark.parametrize(
        "test_data",
        [
            (f"{AGG_ADAPTER_NAME}:host", (AGG_ADAPTER_NAME, ["host"])),
            (
                f"{AGG_ADAPTER_NAME}:host, ip, other",
                (AGG_ADAPTER_NAME, ["host", "ip", "other"]),
            ),
            ("host, ip, other", (AGG_ADAPTER_NAME, ["host", "ip", "other"])),
            ("adapter1:host, ip, other", ("adapter1", ["host", "ip", "other"])),
            (":host", (AGG_ADAPTER_NAME, ["host"])),
        ],
        scope="class",
    )
    def test_split_search(self, apiobj, test_data):
        search, exp = test_data
        result = apiobj.fields.split_search(value=search)
        assert result == exp

    def test_split_search_adapter_specific(self, apiobj):
        exp = ("tanium_asset", ["adapters_data.tanium_asset_adapter.installed_software"])
        search = "adapters_data.tanium_asset_adapter.installed_software"
        result = apiobj.fields.split_search(value=search)
        assert result == exp

    @pytest.mark.parametrize(
        "test_data",
        [
            (f"{AGG_ADAPTER_NAME}:host", [(AGG_ADAPTER_NAME, ["host"])]),
            (
                f"{AGG_ADAPTER_NAME}:host, ip, other",
                [(AGG_ADAPTER_NAME, ["host", "ip", "other"])],
            ),
            ("host, ip, other", [(AGG_ADAPTER_NAME, ["host", "ip", "other"])]),
            ("adapter1:host, ip, other", [("adapter1", ["host", "ip", "other"])]),
            (
                [f"{AGG_ADAPTER_NAME}:host", "adapter1:host, ip, other"],
                [(AGG_ADAPTER_NAME, ["host"]), ("adapter1", ["host", "ip", "other"])],
            ),
        ],
        scope="class",
    )
    def test_split_searches(self, apiobj, test_data):
        searches, exp = test_data
        result = apiobj.fields.split_searches(value=searches)
        assert result == exp

    def test_split_search_error(self, apiobj):
        search = f"{AGG_ADAPTER_NAME}:"
        with pytest.raises(ApiError):
            apiobj.fields.split_search(value=search)

    def test_get_field_name_manual(self, apiobj):
        search = "test"
        result = apiobj.fields.get_field_name(
            value=search,
            field_manual=True,
        )
        assert search == result

    def test_get_field_name_error(self, apiobj):
        search = "bad,wolf"
        with pytest.raises(ApiError):
            apiobj.fields.get_field_name(value=search)

    def test_get_field_name(self, apiobj):
        search = "last_seen"
        exp = "specific_data.data.last_seen"
        result = apiobj.fields.get_field_name(value=search)
        assert result == exp

    def test_validate(self, apiobj):
        exp = apiobj.fields_default + [
            "specific_data.data",
            "specific_data.data.first_fetch_time",
        ]
        result = apiobj.fields.validate(
            fields=["last_seen"],
            fields_regex=["^first_fetch_time$"],
            fields_manual=["specific_data.data"],
            fields_default=True,
        )
        assert result == exp

    def test_validate_root(self, apiobj):
        result = apiobj.fields.validate(fields_root="agg")
        assert len(result) > 1

    def test_validate_defaults(self, apiobj):
        exp = apiobj.fields_default
        result = apiobj.fields.validate()
        assert exp == result

    def test_validate_fuzzy(self, apiobj):
        result = apiobj.fields.validate(fields_fuzzy="last seen", fields_default=False)
        assert "specific_data.data.last_seen" in result

    def test_validate_error(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.fields.validate(fields_default=False)

    def test_fuzzy_filter_contains(self, apiobj):
        schemas = apiobj.fields.get()["agg"]
        matches = apiobj.fields.fuzzy_filter(search="last", schemas=schemas, names=True)
        assert isinstance(matches, list) and matches
        for x in matches:
            assert isinstance(x, str)
        assert len(matches) > 1
        assert "specific_data.data.last_seen" in matches

    def test_fuzzy_filter_token(self, apiobj):
        schemas = apiobj.fields.get()["agg"]
        matches = apiobj.fields.fuzzy_filter(
            search="last seen", schemas=schemas, names=True
        )
        assert isinstance(matches, list) and matches
        for x in matches:
            assert isinstance(x, str)
        assert len(matches) > 1
        assert "specific_data.data.last_seen" in matches

    def test_fuzzy_filter_partial(self, apiobj):
        schemas = apiobj.fields.get()["agg"]
        matches = apiobj.fields.fuzzy_filter(search="bd", schemas=schemas, names=True)
        assert isinstance(matches, list) and matches
        for x in matches:
            assert isinstance(x, str)
        assert len(matches) > 1
        assert "specific_data.data.id" in matches


class TestFieldsDevices(FieldsPrivate, FieldsPublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices


class TestFieldsUsers(FieldsPrivate, FieldsPublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users


def val_source(obj):
    source = obj.pop("source", {})
    assert isinstance(source, dict)

    if source:
        source_key = source.pop("key")
        assert isinstance(source_key, str)

        source_options = source.pop("options")
        assert isinstance(source_options, dict)

        options_allow = source_options.pop("allow-custom-option")
        assert isinstance(options_allow, bool)

        assert not source, source
        assert not source_options, source_options
