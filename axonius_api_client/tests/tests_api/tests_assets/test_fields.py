# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy

import pytest

from axonius_api_client.api import json_api
from axonius_api_client.constants.fields import AGG_ADAPTER_ALTS, AGG_ADAPTER_NAME
from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import FIELD_FORMATS, SCHEMA_FIELD_FORMATS, SCHEMA_TYPES
from ...utils import get_schema, get_schemas


def pop_hyperlinks(schema):
    hyperlinks = schema.pop("hyperlinks", None)
    assert isinstance(hyperlinks, str) or hyperlinks is None


def pop_enum(schema):
    enums = schema.pop("enum", [])
    assert isinstance(enums, list) or enums is None
    for enum in enums or []:
        assert isinstance(enum, (str, int, dict))


class TestFieldsPrivate:
    @pytest.fixture(params=["api_devices", "api_users", "api_vulnerabilities"], scope="class")
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

    def test_private_get(self, apiobj):
        fields = apiobj.fields._get()
        assert isinstance(fields, json_api.generic.Metadata)
        self.val_raw_fields(fields=fields.document_meta)

    def val_raw_fields(self, fields):
        fields = copy.deepcopy(fields)
        assert isinstance(fields, dict)

        schema = fields.pop("schema")
        assert isinstance(schema, dict)

        generic = fields.pop("generic", [])
        assert isinstance(generic, list)

        self.val_raw_adapter_fields(adapter="generic", adapter_fields=generic)

        generic_schema = schema.pop("generic", True)
        assert isinstance(generic_schema, dict)
        self.val_raw_schema(adapter="generic", schema=generic_schema)

        specific = fields.pop("specific")
        assert isinstance(specific, dict)

        specific_schema = schema.pop("specific")
        assert isinstance(specific_schema, dict)

        for adapter, adapter_fields in specific.items():
            self.val_raw_adapter_fields(adapter=adapter, adapter_fields=adapter_fields)
            adapter_schema = specific_schema.pop(adapter)
            # TBD: in 4.6 some of the schemas are None, investigating
            if adapter_schema is not None:
                self.val_raw_schema(adapter=adapter, schema=adapter_schema)

        # assert not fields
        # assert not schema

    def val_raw_schema(self, adapter, schema):
        assert isinstance(schema, dict)

        items = schema.pop("items")
        assert isinstance(items, list)

        required = schema.pop("required", [])
        assert isinstance(required, list)

        stype = schema.pop("type")
        assert stype == "array"

        # assert not schema, list(schema)

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
            if isinstance(sort, dict):
                sort_desc = sort.pop("desc")
                assert isinstance(sort_desc, bool)
                sort_field = sort.pop("field")
                assert isinstance(sort_field, str)
                # assert not sort
            else:
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

            pop_enum(field)

            items = field.pop("items", {})
            assert isinstance(items, dict)

            # added in 3.10?
            filterable = field.pop("filterable")
            assert isinstance(filterable, bool)

            # added in 3.11?
            generic = field.pop("generic", True)
            assert isinstance(generic, bool)

            self.val_raw_items(adapter=f"{adapter}:{name}", items=items)

            # 4.0
            dvi = field.pop("dynamic_value_identifier", None)
            assert isinstance(dvi, str) or dvi is None

            # 4.3
            are_values_cached = field.pop("are_values_cached", False)
            assert isinstance(are_values_cached, bool)

            # 4.5
            parse_json_attrs = field.pop("parse_json_attrs", False)
            assert isinstance(parse_json_attrs, bool)

            show_all_results = field.pop("show_all_results", False)
            assert isinstance(show_all_results, bool)

            val_source(obj=field)

            # 4.6 {'base_table_name': None, 'part_of_table': True}
            base_table_name = field.pop("base_table_name", None)
            assert isinstance(base_table_name, str) or base_table_name is None

            part_of_table = field.pop("part_of_table", False)
            assert isinstance(part_of_table, bool)

            # 2022-04-09 {'flatten': True}
            flatten = field.pop("flatten", False)
            assert isinstance(flatten, bool)

            # 2022-09-02
            view_type = field.pop("view_type", None)
            assert isinstance(view_type, str) or view_type is None
            # 2022-09-02
            info = field.pop("info", None)
            assert isinstance(info, str) or info is None
            pop_hyperlinks(schema=field)
            # assert not field, list(field)

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

            pop_enum(items)

            # added in 3.11?
            generic = items.pop("generic", True)
            assert isinstance(generic, bool)

            sub_items = items.pop("items", [])
            assert isinstance(sub_items, list) or isinstance(sub_items, dict)

            # 4.0
            dvi = items.pop("dynamic_value_identifier", None)
            assert isinstance(dvi, str) or dvi is None

            # 4.3
            are_values_cached = items.pop("are_values_cached", False)
            assert isinstance(are_values_cached, bool)

            # 4.5
            parse_json_attrs = items.pop("parse_json_attrs", False)
            assert isinstance(parse_json_attrs, bool)

            show_all_results = items.pop("show_all_results", False)
            assert isinstance(show_all_results, bool)

            # 4.6 {'base_table_name': None, 'part_of_table': True}
            base_table_name = items.pop("base_table_name", None)
            assert isinstance(base_table_name, str) or base_table_name is None

            part_of_table = items.pop("part_of_table", False)
            assert isinstance(part_of_table, bool)

            # assert not items, list(items)

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


class TestFieldsPublic:
    @pytest.fixture(params=["api_devices", "api_users"], scope="class")
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

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
        if isinstance(sort, dict):
            sort_desc = sort.pop("desc")
            assert isinstance(sort_desc, bool)
            sort_field = sort.pop("field")
            assert isinstance(sort_field, str)
            # assert not sort
        else:
            assert isinstance(sort, bool)

        unique = schema.pop("unique", False)
        assert isinstance(unique, bool)

        branched = schema.pop("branched", False)
        assert isinstance(branched, bool)

        dynamic = schema.pop("dynamic", False)
        assert isinstance(dynamic, bool)

        is_complex = schema.pop("is_complex")
        assert isinstance(is_complex, bool)

        pop_enum(schema)

        is_agg = schema.pop("is_agg")
        assert isinstance(is_agg, bool)

        is_all = schema.pop("is_all")
        assert isinstance(is_all, bool)

        is_details = schema.pop("is_details")
        assert isinstance(is_details, bool)

        expr_field_type = schema.pop("expr_field_type")
        assert isinstance(expr_field_type, str)

        sub_fields = schema.pop("sub_fields", [])
        assert isinstance(sub_fields, list)

        items = schema.pop("items", {})
        assert isinstance(items, dict)

        # added in 3.10?
        filterable = schema.pop("filterable", False)
        assert isinstance(filterable, bool)

        # 3.11
        generic = schema.pop("generic", True)
        assert isinstance(generic, bool)

        # 4.0
        val_source(obj=schema)

        # 4.0
        dvi = schema.pop("dynamic_value_identifier", None)
        assert isinstance(dvi, str) or dvi is None

        # 4.3
        are_values_cached = schema.pop("are_values_cached", False)
        assert isinstance(are_values_cached, bool)

        # 4.5
        parse_json_attrs = schema.pop("parse_json_attrs", False)
        assert isinstance(parse_json_attrs, bool)

        show_all_results = schema.pop("show_all_results", False)
        assert isinstance(show_all_results, bool)

        # 4.6 {'base_table_name': None, 'part_of_table': True}
        base_table_name = schema.pop("base_table_name", None)
        assert isinstance(base_table_name, str) or base_table_name is None

        part_of_table = schema.pop("part_of_table", False)
        assert isinstance(part_of_table, bool)

        # 2022-04-09 {'flatten': True}
        flatten = schema.pop("flatten", False)
        assert isinstance(flatten, bool)

        if is_complex:
            if name != "all" and not name.endswith("raw_data"):
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
            pop_enum(items)

            # 3.11
            generic = items.pop("generic", True)
            assert isinstance(generic, bool)

            # 4.0
            dvi = items.pop("dynamic_value_identifier", None)
            assert isinstance(dvi, str) or dvi is None

            # 4.3
            are_values_cached = items.pop("are_values_cached", False)
            assert isinstance(are_values_cached, bool)

            # 4.5
            parse_json_attrs = items.pop("parse_json_attrs", False)
            assert isinstance(parse_json_attrs, bool)

            # 4.6 {'base_table_name': None, 'part_of_table': True}
            base_table_name = items.pop("base_table_name", None)
            assert isinstance(base_table_name, str) or base_table_name is None

            part_of_table = items.pop("part_of_table", False)
            assert isinstance(part_of_table, bool)

            show_all_results = items.pop("show_all_results", False)
            assert isinstance(show_all_results, bool)

            # assert not items

        # 2022-09-02
        view_type = schema.pop("view_type", None)
        assert isinstance(view_type, str) or view_type is None
        # 2022-09-02
        info = schema.pop("info", None)
        assert isinstance(info, str) or info is None
        pop_hyperlinks(schema=schema)
        # assert not schema, list(schema)

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
        found = [x for x in schemas if x["name_base"] == search]
        if not found:
            pytest.skip(f"field {search} not found")
        exp = found[0]
        result = apiobj.fields.get_field_schema(value=search, schemas=schemas)
        assert exp == result

    def test_get_field_names_re(self, apiobj):
        search = ["seen"]
        get_schema(apiobj=apiobj, field="specific_data.data.last_seen")
        result = apiobj.fields.get_field_names_re(value=search)
        assert "specific_data.data.last_seen" in result

    def test_get_field_names_eq(self, apiobj):
        get_schema(apiobj=apiobj, field="specific_data.data.last_seen")
        search = ["specific_data.data.id", "last_seen"]
        exp = []
        schemas = get_schemas(apiobj=apiobj)
        for i in search:
            exp += [x["name_qual"] for x in schemas if x["name_base"] == i or x["name_qual"] == i]
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
        get_schema(apiobj=apiobj, field="specific_data.data.last_seen")
        search = "last_seen"
        exp = "specific_data.data.last_seen"
        result = apiobj.fields.get_field_name(value=search)
        assert result == exp

    def test_validate(self, apiobj):
        get_schema(apiobj=apiobj, field="specific_data.data.last_seen")
        get_schema(apiobj=apiobj, field="specific_data.data.first_fetch_time")

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

    def test_validate_fields_error_true(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.fields.validate(fields_default=False, fields_error=True)

        with pytest.raises(NotFoundError):
            apiobj.fields.validate(fields=["xxx"], fields_default=False, fields_error=True)

    def test_validate_fields_error_false(self, apiobj):
        fields = apiobj.fields.validate(fields_default=False, fields_error=False)
        # assert not fields

        fields = apiobj.fields.validate(fields=["xxx"], fields_default=False, fields_error=False)
        assert fields == ["xxx"]

    def test_validate_fuzzy(self, apiobj):
        get_schema(apiobj=apiobj, field="specific_data.data.last_seen")
        result = apiobj.fields.validate(fields_fuzzy="lastseen", fields_default=False)
        assert "specific_data.data.last_seen" in result

    def test_validate_error(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.fields.validate(fields_default=False)


class TestFuzzyFieldsDevices:
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices

    def test_validate_fuzzy_str(self, apiobj):
        get_schema(apiobj=apiobj, field="specific_data.data.os.type")
        result = apiobj.fields.validate(fields_fuzzy="os.type", fields_default=False)
        assert all(["os.type" in x for x in result])

    def test_validate_fuzzy_fail(self, apiobj):
        with pytest.raises(NotFoundError) as exc:
            apiobj.fields.validate(fields="os", fields_default=False)
        assert "Maybe you meant" in str(exc.value)


def val_source(obj):
    source = obj.pop("source", {})
    assert isinstance(source, dict)

    if source:
        source_key = source.pop("key")
        assert isinstance(source_key, str)

        source_options = source.pop("options", {})
        assert isinstance(source_options, dict)

        options_allow = source_options.pop("allow-custom-option", False)
        assert isinstance(options_allow, bool)

        # assert not source, source
        # assert not source_options, source_options
