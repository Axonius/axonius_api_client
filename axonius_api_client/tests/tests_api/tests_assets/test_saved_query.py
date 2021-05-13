# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.assets."""
import copy
import datetime
import json

import pytest

from axonius_api_client.api import json_api
from axonius_api_client.constants.api import GUI_PAGE_SIZES
from axonius_api_client.constants.general import SIMPLE
from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import QUERIES
from ...utils import get_schema


class SavedQueryPrivate:
    def test_private_get(self, apiobj):
        result = apiobj.saved_query._get()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, json_api.saved_queries.SavedQuery)
            validate_sq(item.to_dict())


class SavedQueryPublic:
    def test_get_no_generator(self, apiobj):
        rows = apiobj.saved_query.get(generator=False)
        assert not rows.__class__.__name__ == "generator"
        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)

    def test_get_generator(self, apiobj):
        gen = apiobj.saved_query.get(generator=True)
        assert gen.__class__.__name__ == "generator"
        assert not isinstance(gen, list)

        rows = [x for x in gen]
        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)

    def test_get_tags(self, apiobj):
        tags = apiobj.saved_query.get_tags()
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, str)

    def test_get_by_name(self, apiobj):
        sq = apiobj.saved_query.get()[0]
        value = sq["name"]
        row = apiobj.saved_query.get_by_name(value=value)
        assert isinstance(row, dict)
        assert row["name"] == value

    def test_get_by_name_error(self, apiobj):
        value = "badwolf_yyyyyyyyyyyy"
        with pytest.raises(NotFoundError):
            apiobj.saved_query.get_by_name(value=value)

    def test_get_by_uuid(self, apiobj):
        sq = apiobj.saved_query.get()[0]
        value = sq["uuid"]
        row = apiobj.saved_query.get_by_uuid(value=value)
        assert isinstance(row, dict)
        assert row["uuid"] == value

    def test_get_by_uuid_error(self, apiobj):
        value = "badwolf_xxxxxxxxxxxxx"
        with pytest.raises(NotFoundError):
            apiobj.saved_query.get_by_uuid(value=value)

    def test_get_by_tags(self, apiobj):
        tags = [y for x in apiobj.saved_query.get() for y in x.get("tags", [])]
        value = tags[0]
        rows = apiobj.saved_query.get_by_tags(value=value)
        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, dict)
            assert value in row["tags"]

    def test_get_by_tags_error(self, apiobj):
        value = "badwolf_wwwwwwww"
        with pytest.raises(NotFoundError):
            apiobj.saved_query.get_by_tags(value=value)

    @pytest.fixture(scope="class")
    def sq_fixture(self, apiobj):
        get_schema(apiobj=apiobj, field="specific_data.data.last_seen")
        field_simple = apiobj.FIELD_SIMPLE

        name = "badwolf torked"
        fields = ["adapters", "last_seen", "id", field_simple]

        sort_field = field_simple
        colfilters = {field_simple: "a"}
        sort_desc = False
        gui_page_size = GUI_PAGE_SIZES[-1]
        tags = ["badwolf1", "badwolf2"]
        description = "badwolf torked"
        query = QUERIES["not_last_seen_day"]

        try:
            apiobj.saved_query.delete_by_name(value=name)
        except NotFoundError:
            pass

        row = apiobj.saved_query.add(
            name=name,
            fields=fields,
            sort_field=sort_field,
            sort_descending=sort_desc,
            column_filters=colfilters,
            gui_page_size=gui_page_size,
            tags=tags,
            description=description,
            query=query,
        )
        validate_sq(row)

        assert row["name"] == name
        assert row["query_type"] == "saved"
        assert row["tags"] == tags
        assert row["description"] == description
        assert row["private"] is False
        assert row["view"]["query"]["filter"] == query
        assert row["view"]["query"]["onlyExpressionsFilter"] == query
        assert row["view"]["query"]["expressions"] == []
        assert row["view"]["pageSize"] == gui_page_size
        assert row["view"]["colFilters"] == colfilters
        assert row["view"]["sort"]["field"] == sort_field
        assert row["view"]["sort"]["desc"] == sort_desc

        yield row

        try:
            apiobj.saved_query.delete_by_name(value=name)
        except NotFoundError:
            pass

    def test_add_remove(self, apiobj, sq_fixture):
        row = apiobj.saved_query.delete_by_name(value=sq_fixture["name"])
        assert isinstance(row, dict)
        assert row["uuid"] == sq_fixture["uuid"]

        with pytest.raises(NotFoundError):
            apiobj.saved_query.get_by_name(value=sq_fixture["name"])

    def test_add_error_no_fields(self, apiobj):
        name = "badwolf_nnnnnnnnnnnnn"
        with pytest.raises(ApiError):
            apiobj.saved_query.add(name=name, fields_default=False)

    def test_add_error_bad_sort_field(self, apiobj):
        name = "badwolf_sssssssssssss"
        fields = "last_seen"
        sort_field = "badwolf"
        with pytest.raises(ApiError):
            apiobj.saved_query.add(name=name, fields=fields, sort_field=sort_field)

    def test_add_error_bad_colfilter(self, apiobj):
        name = "badwolf_ttttttttttt"
        fields = "last_seen"
        colfilters = {"badwolf": "badwolf"}
        with pytest.raises(ApiError):
            apiobj.saved_query.add(name=name, fields=fields, column_filters=colfilters)


class TestSavedQueryDevices(SavedQueryPrivate, SavedQueryPublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices


class TestSavedQueryUsers(SavedQueryPrivate, SavedQueryPublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users


def validate_qexpr(qexpr, asset):
    assert isinstance(qexpr, dict)

    compop = qexpr.pop("compOp")
    assert isinstance(compop, str)

    field = qexpr.pop("field")
    assert isinstance(field, str)

    idx = qexpr.pop("i", 0)
    assert isinstance(idx, int)

    leftbracket = qexpr.pop("leftBracket", 0)
    assert isinstance(leftbracket, (int, bool))

    rightbracket = qexpr.pop("rightBracket", 0)
    assert isinstance(rightbracket, (int, bool))

    logicop = qexpr.pop("logicOp")
    assert isinstance(logicop, str)

    notflag = qexpr.pop("not")
    assert isinstance(notflag, bool)

    value = qexpr.pop("value")
    assert isinstance(value, SIMPLE) or value is None

    obj = qexpr.pop("obj", False)
    assert isinstance(obj, bool)

    nesteds = qexpr.pop("nested", [])
    assert isinstance(nesteds, list)

    fieldtype = qexpr.pop("fieldType", "")
    assert isinstance(fieldtype, str)

    children = qexpr.pop("children", [])  # new in 2.15
    assert isinstance(children, list)  # new in 2.15

    filtered_adapters = qexpr.pop("filteredAdapters", {})
    assert isinstance(filtered_adapters, dict) or filtered_adapters is None

    context = qexpr.pop("context", "")  # new in 2.15
    assert isinstance(context, str)

    timestamp = qexpr.pop("timestamp", "")
    assert isinstance(timestamp, str)

    brackweight = qexpr.pop("bracketWeight", 0)
    assert isinstance(brackweight, int)

    qfilter = qexpr.pop("filter", "")
    assert isinstance(qfilter, str)

    for nested in nesteds:
        validate_nested(nested, asset)

    for child in children:
        validate_nested(child, asset)

    assert not qexpr, list(qexpr)


def validate_nested(nested, asset):
    assert isinstance(nested, dict)

    nfiltered_adapters = nested.pop("filteredAdapters", {})
    assert isinstance(nfiltered_adapters, dict) or nfiltered_adapters is None

    ncondition = nested.pop("condition")
    assert isinstance(ncondition, str)

    nexpr = nested.pop("expression")
    assert isinstance(nexpr, dict)

    nidx = nested.pop("i")
    assert isinstance(nidx, int)

    assert not nested, list(nested)


def validate_sq(asset):
    asset = copy.deepcopy(asset)
    assert isinstance(asset, dict)

    original = copy.deepcopy(asset)
    assert original == asset

    assert asset["query_type"] in ["saved"]

    date_fetched = asset.pop("date_fetched")
    assert isinstance(date_fetched, str)

    last_updated = asset.pop("last_updated", None)
    assert isinstance(last_updated, (str, datetime.datetime, type(None)))

    name = asset.pop("name")
    assert isinstance(name, str)

    query_type = asset.pop("query_type")
    assert isinstance(query_type, str)

    user_id = asset.pop("user_id")
    assert isinstance(user_id, str)

    uuid = asset.pop("uuid")
    assert isinstance(uuid, str)

    description = asset.pop("description")
    assert isinstance(description, str) or description is None

    timestamp = asset.pop("timestamp", "")
    assert isinstance(timestamp, (str, type(None)))

    archived = asset.pop("archived", False)  # added in 2.15
    assert isinstance(archived, bool)

    updated_by_str = asset.pop("updated_by")
    assert isinstance(updated_by_str, str)

    updated_by = json.loads(updated_by_str)
    assert isinstance(updated_by, dict)

    updated_by_deleted = updated_by.pop("deleted")
    assert isinstance(updated_by_deleted, bool)

    updated_str_keys_req = [
        "first_name",
        "last_name",
        "source",
        "user_name",
    ]
    for updated_str_key in updated_str_keys_req:
        val = updated_by.pop(updated_str_key)
        assert isinstance(val, (str, int, float)) or val is None

    updated_str_keys_opt = [
        "_id",
        "last_updated",
        "password",
        "pic_name",
        "role_id",
        "salt",
    ]
    for updated_str_key in updated_str_keys_opt:
        val = updated_by.pop(updated_str_key, None)
        assert isinstance(val, (str, int, float)) or val is None

    assert not updated_by

    tags = asset.pop("tags", [])
    assert isinstance(tags, list)
    for tag in tags:
        assert isinstance(tag, str)

    predefined = asset.pop("predefined", False)
    assert isinstance(predefined, bool)

    private = asset.pop("private", False)
    assert isinstance(private, bool)

    view = asset.pop("view")
    assert isinstance(view, dict)

    colsizes = view.pop("coloumnSizes", [])
    assert isinstance(colsizes, list)

    for x in colsizes:
        assert isinstance(x, int)

    fields = view.pop("fields")
    assert isinstance(fields, list)

    for x in fields:
        assert isinstance(x, str)

    page = view.pop("page", 0)
    assert isinstance(page, int)

    pagesize = view.pop("pageSize", 0)
    assert isinstance(pagesize, int)

    sort = view.pop("sort")
    assert isinstance(sort, dict)

    sort_desc = sort.pop("desc")
    assert isinstance(sort_desc, bool)

    sort_field = sort.pop("field")
    assert isinstance(sort_field, str)

    query = view.pop("query")
    assert isinstance(query, dict)

    colfilters = view.pop("colFilters", {})
    assert isinstance(colfilters, dict)
    for k, v in colfilters.items():
        assert isinstance(k, str)
        assert isinstance(v, str)

    qfilter = query.pop("filter")
    assert isinstance(qfilter, str) or qfilter is None

    qexprs = query.pop("expressions", [])
    assert isinstance(qexprs, list)

    qmeta = query.pop("meta", {})
    assert isinstance(qmeta, dict)

    qonlyexprfilter = query.pop("onlyExpressionsFilter", "")
    assert isinstance(qonlyexprfilter, str)

    qsearch = query.pop("search", None)
    assert qsearch is None or isinstance(qsearch, str)

    historical = view.pop("historical", None)
    assert historical is None or isinstance(historical, SIMPLE)

    # 3.6+
    excluded_adapters = view.pop("colExcludedAdapters", {})
    assert isinstance(excluded_adapters, dict)

    # 4.0
    always_cached = asset.pop("always_cached")
    assert isinstance(always_cached, bool)
    asset_scope = asset.pop("asset_scope")
    assert isinstance(asset_scope, bool)
    is_asset_scope_query_ready = asset.pop("is_asset_scope_query_ready")
    assert isinstance(is_asset_scope_query_ready, bool)
    is_referenced = asset.pop("is_referenced")
    assert isinstance(is_referenced, bool)
    _id = asset.pop("id")
    assert isinstance(_id, str) and _id

    for qexpr in qexprs:
        validate_qexpr(qexpr, asset)

    assert not query, list(query)
    assert not sort, list(sort)
    assert not view, list(view)
    assert not asset, list(asset)
