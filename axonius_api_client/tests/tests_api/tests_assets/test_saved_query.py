# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.assets."""
import copy
import json

import pytest

from axonius_api_client.api.assets.saved_query import check_gui_page_size
from axonius_api_client.constants import GUI_PAGE_SIZES, SIMPLE
from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import QUERIES


def load_test_data(apiobj):
    """Pass."""
    apiobj.TEST_DATA = getattr(apiobj, "TEST_DATA", {})

    if not apiobj.TEST_DATA.get("saved_queries"):
        apiobj.TEST_DATA["saved_queries"] = apiobj.saved_query.get()

    return apiobj


def test_check_gui_page_size_error():
    """Pass."""
    gui_page_size = 9999
    with pytest.raises(ApiError):
        check_gui_page_size(size=gui_page_size)


class SavedQueryPrivate:
    """Pass."""

    def test_private_get(self, apiobj):
        """Pass."""
        result = apiobj.saved_query._get()
        assert isinstance(result, dict)

        rows = result["assets"]
        assert isinstance(rows, list)

        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)


class SavedQueryPublic:
    """Pass."""

    def test_get_no_generator(self, apiobj):
        """Pass."""
        rows = apiobj.saved_query.get(generator=False)
        assert not rows.__class__.__name__ == "generator"
        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)

    def test_get_generator(self, apiobj):
        """Pass."""
        gen = apiobj.saved_query.get(generator=True)
        assert gen.__class__.__name__ == "generator"
        assert not isinstance(gen, list)

        rows = [x for x in gen]
        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)

    def test_get_max_pages(self, apiobj):
        """Pass."""
        rows = apiobj.saved_query.get(max_pages=1, page_size=2)
        assert isinstance(rows, list)
        assert len(rows) == 2
        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)

    def test_get_max_rows(self, apiobj):
        """Pass."""
        rows = apiobj.saved_query.get(max_rows=1)
        assert isinstance(rows, list)
        assert len(rows) == 1
        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)

    def test_get_tags(self, apiobj):
        """Pass."""
        tags = apiobj.saved_query.get_tags()
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, str)

    def test_get_by_name(self, apiobj):
        """Pass."""
        sq = apiobj.TEST_DATA["saved_queries"][0]
        value = sq["name"]
        row = apiobj.saved_query.get_by_name(value=value)
        assert isinstance(row, dict)
        assert row["name"] == value

    def test_get_by_name_error(self, apiobj):
        """Pass."""
        value = "badwolf_yyyyyyyyyyyy"
        with pytest.raises(NotFoundError):
            apiobj.saved_query.get_by_name(value=value)

    def test_get_by_uuid(self, apiobj):
        """Pass."""
        sq = apiobj.TEST_DATA["saved_queries"][0]
        value = sq["uuid"]
        row = apiobj.saved_query.get_by_uuid(value=value)
        assert isinstance(row, dict)
        assert row["uuid"] == value

    def test_get_by_uuid_error(self, apiobj):
        """Pass."""
        value = "badwolf_xxxxxxxxxxxxx"
        with pytest.raises(NotFoundError):
            apiobj.saved_query.get_by_uuid(value=value)

    def test_get_by_tags(self, apiobj):
        """Pass."""
        tags = [y for x in apiobj.TEST_DATA["saved_queries"] for y in x.get("tags", [])]
        value = tags[0]
        rows = apiobj.saved_query.get_by_tags(value=value)
        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, dict)
            assert value in row["tags"]

    def test_get_by_tags_error(self, apiobj):
        """Pass."""
        value = "badwolf_wwwwwwww"
        with pytest.raises(NotFoundError):
            apiobj.saved_query.get_by_tags(value=value)

    @pytest.fixture(scope="class")
    def sq_fixture(self, apiobj):
        """Pass."""
        field_simple = apiobj.TEST_DATA["field_simple"]

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

        row_original = apiobj.saved_query.add(
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
        assert isinstance(row_original, dict)
        row_validate = copy.deepcopy(row_original)
        row = copy.deepcopy(row_original)
        validate_sq(row_validate)

        row_name = row.pop("name")
        assert row_name == name

        row_query_type = row.pop("query_type")
        assert row_query_type == "saved"

        row_tags = row.pop("tags")
        assert row_tags == tags

        row_description = row.pop("description")
        assert row_description == description

        row_view = row.pop("view")
        assert isinstance(row_view, dict)

        row_archived = row.pop("archived")
        assert row_archived is False

        row_date_fetched = row.pop("date_fetched")
        assert isinstance(row_date_fetched, str)

        row_user_id = row.pop("user_id")
        assert isinstance(row_user_id, str)

        row_last_updated = row.pop("last_updated")
        assert isinstance(row_last_updated, str)

        row_uuid = row.pop("uuid")
        assert isinstance(row_uuid, str)

        row_updated_by = row.pop("updated_by")
        assert isinstance(row_updated_by, str)

        row_updated_by_json = json.loads(row_updated_by)
        assert isinstance(row_updated_by_json, dict)

        row_private = row.pop("private", False)
        assert isinstance(row_private, bool)

        assert not row

        # row["view"]
        row_view_sort = row_view.pop("sort")
        assert isinstance(row_view_sort, dict)

        row_view_fields = row_view.pop("fields")
        assert isinstance(row_view_fields, list)

        row_view_query = row_view.pop("query")
        assert isinstance(row_view_query, dict)

        row_view_page_size = row_view.pop("pageSize")
        assert row_view_page_size == gui_page_size

        row_view_colfilters = row_view.pop("colFilters")
        assert row_view_colfilters == colfilters

        assert not row_view

        # row["view"]["sort"]
        row_view_sort_field = row_view_sort.pop("field")
        assert row_view_sort_field == sort_field

        row_view_sort_desc = row_view_sort.pop("desc")
        assert row_view_sort_desc == sort_desc

        assert not row_view_sort

        # row["view"]["query"]
        row_view_query_filter = row_view_query.pop("filter")
        assert row_view_query_filter == query

        row_view_query_expressions = row_view_query.pop("expressions")
        assert row_view_query_expressions == []

        # TBD
        # row_view_query_search = row_view_query.pop("search")
        # assert row_view_query_search == ""

        assert not row_view_query
        yield row_original
        try:
            apiobj.saved_query.delete_by_name(value=name)
        except NotFoundError:
            pass

    def test_add_remove(self, apiobj, sq_fixture):
        """Pass."""
        row = apiobj.saved_query.delete_by_name(value=sq_fixture["name"])
        assert isinstance(row, dict)
        assert row["uuid"] == sq_fixture["uuid"]

        with pytest.raises(NotFoundError):
            apiobj.saved_query.get_by_name(value=sq_fixture["name"])

    def test_add_error_no_fields(self, apiobj):
        """Pass."""
        name = "badwolf_nnnnnnnnnnnnn"
        with pytest.raises(ApiError):
            apiobj.saved_query.add(name=name, fields_default=False)

    def test_add_error_bad_sort_field(self, apiobj):
        """Pass."""
        name = "badwolf_sssssssssssss"
        fields = "last_seen"
        sort_field = "badwolf"
        with pytest.raises(ApiError):
            apiobj.saved_query.add(name=name, fields=fields, sort_field=sort_field)

    def test_add_error_bad_colfilter(self, apiobj):
        """Pass."""
        name = "badwolf_ttttttttttt"
        fields = "last_seen"
        colfilters = {"badwolf": "badwolf"}
        with pytest.raises(ApiError):
            apiobj.saved_query.add(name=name, fields=fields, column_filters=colfilters)


class TestSavedQueryDevices(SavedQueryPrivate, SavedQueryPublic):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return load_test_data(api_devices)


class TestSavedQueryUsers(SavedQueryPrivate, SavedQueryPublic):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return load_test_data(api_users)


def validate_qexpr(qexpr, asset):
    """Pass."""
    assert isinstance(qexpr, dict)
    # XXX build a query builder :)

    compop = qexpr.pop("compOp")
    assert isinstance(compop, str)

    field = qexpr.pop("field")
    assert isinstance(field, str)

    idx = qexpr.pop("i", 0)
    assert isinstance(idx, int)

    leftbracket = qexpr.pop("leftBracket")
    assert isinstance(leftbracket, bool)

    rightbracket = qexpr.pop("rightBracket")
    assert isinstance(rightbracket, bool)

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
    """Pass."""
    assert isinstance(nested, dict)

    # new in 2.10, unsure of
    # if not None, dict with keys: clearAll, selectAll, selectedValues
    # XXX figure this out
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
    """Pass."""
    assert isinstance(asset, dict)

    original = copy.deepcopy(asset)
    assert original == asset

    assert asset["query_type"] in ["saved"]

    date_fetched = asset.pop("date_fetched")
    assert isinstance(date_fetched, str)

    last_updated = asset.pop("last_updated", "")
    assert isinstance(last_updated, str)

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
    assert isinstance(timestamp, str)

    archived = asset.pop("archived", False)  # added in 2.15
    assert isinstance(archived, bool)

    updated_by_str = asset.pop("updated_by")
    assert isinstance(updated_by_str, str)

    updated_by = json.loads(updated_by_str)
    assert isinstance(updated_by, dict)

    updated_by_deleted = updated_by.pop("deleted")
    assert isinstance(updated_by_deleted, bool)

    updated_str_keys = ["username", "source", "first_name", "last_name"]
    for updated_str_key in updated_str_keys:
        val = updated_by.pop(updated_str_key)
        assert isinstance(val, str)

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

    for qexpr in qexprs:
        validate_qexpr(qexpr, asset)

    assert not query, list(query)
    assert not sort, list(sort)
    assert not view, list(view)
    assert not asset, list(asset)
