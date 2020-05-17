# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest
import requests

from axonius_api_client.api import mixins
from axonius_api_client.constants import MAX_PAGE_SIZE
from axonius_api_client.exceptions import (
    JsonError,
    JsonInvalid,
    NotFoundError,
    ResponseNotOk,
)
from axonius_api_client.tools import listify

from ...meta import QUERIES


def load_test_data(apiobj):
    """Pass."""
    apiobj.TEST_DATA = getattr(apiobj, "TEST_DATA", {})

    if not apiobj.TEST_DATA.get("fields_map"):
        apiobj.TEST_DATA["fields_map"] = fields_map = apiobj.fields.get()

    if not apiobj.TEST_DATA.get("assets"):
        apiobj.TEST_DATA["assets"] = apiobj.get(max_rows=4000, fields_map=fields_map)

    if not apiobj.TEST_DATA.get("saved_queries"):
        apiobj.TEST_DATA["saved_queries"] = apiobj.saved_query.get()

    return apiobj


class ModelMixinsBase:
    """Pass."""

    def test_model_json(self, apiobj):
        """Test that JSON is returned when is_json=True."""
        response = apiobj.request(
            path=apiobj.router.fields,
            method="get",
            raw=False,
            is_json=True,
            error_status=True,
        )
        assert isinstance(response, dict)

    def test_model_raw(self, apiobj):
        """Test that response is returned when raw=True."""
        response = apiobj.request(
            path=apiobj.router.fields,
            method="get",
            raw=True,
            is_json=True,
            error_status=True,
        )
        assert isinstance(response, requests.Response)

    def test_model_text(self, apiobj):
        """Test that str is returned when raw=False and is_json=False."""
        response = apiobj.request(
            path=apiobj.router.fields,
            method="get",
            raw=False,
            is_json=False,
            error_status=True,
        )
        assert isinstance(response, str)

    def test_model_json_error(self, apiobj):
        """Test exc thrown when json has error status."""
        with pytest.raises(JsonError):
            apiobj.request(
                path=apiobj.router.root + "/badwolf", method="get", error_status=False
            )

    def test_model_no_json_error(self, apiobj):
        """Test exc thrown when status code != 200."""
        with pytest.raises(ResponseNotOk):
            apiobj.request(
                path=apiobj.router.root + "/badwolf",
                method="get",
                error_status=True,
                is_json=False,
            )

    def test_model_json_invalid(self, apiobj):
        """Test exc thrown when invalid json."""
        with pytest.raises(JsonInvalid):
            apiobj.request(path="", method="get")

    def test_model_json_invalid_text(self, apiobj):
        """Test that str is returned when is_json=True and error_json_invalid=False."""
        response = apiobj.request(path="", method="get", error_json_invalid=False)
        assert isinstance(response, str)

    def test_model_child(self, apiobj):
        """Pass."""
        child = mixins.ChildMixins(parent=apiobj)
        assert str(apiobj) in str(child)
        assert repr(apiobj) in repr(child)


class AssetsPrivate:
    """Pass."""

    # def test_private_get_page_stop_rows_stop(self, apiobj):
    #     """Pass."""
    #     state = {
    #         "max_rows": None,
    #         "rows_processed": 1,
    #         "stop": True,
    #         "stop_msg": "fakestop",
    #         "max_pages": None,
    #         "page_num": 1,
    #     }
    #     result = apiobj._get_page_stop_rows(row={}, rows=[{}], state=state, store={})
    #     assert result is True

    # def test_private_get_page_stop_fetch_stop(self, apiobj):
    #     """Pass."""
    #     state = {
    #         "max_rows": None,
    #         "rows_processed": 1,
    #         "stop": True,
    #         "stop_msg": "fakestop",
    #         "max_pages": None,
    #         "page_num": 1,
    #     }
    #     result = apiobj._get_page_stop_fetch(rows=[{}], state=state, store={})
    #     assert result is True

    def test_private_get(self, apiobj):
        """Pass."""
        data = apiobj._get(page_size=1)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], list)
        assert len(data["assets"]) == 1

    def test_private_get_normal_query(self, apiobj):
        """Pass."""
        data = apiobj._get(query=QUERIES["not_last_seen_day"], page_size=1)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], list)
        assert len(data["assets"]) == 1

    def test_private_get_cursor(self, apiobj):
        """Pass."""
        data = apiobj._get_cursor(page_size=1)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], list)
        assert len(data["assets"]) == 1

    def test_private_get_cursor_query(self, apiobj):
        """Pass."""
        query = QUERIES["not_last_seen_day"]
        data = apiobj._get_cursor(query=query, page_size=1)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], list)
        assert len(data["assets"]) == 1

    def test_private_get_by_id(self, apiobj):
        """Pass."""
        asset = apiobj.TEST_DATA["assets"][0]
        id = asset["internal_axon_id"]
        data = apiobj._get_by_id(id=id)
        assert isinstance(data, dict)
        assert data["internal_axon_id"] == id

    def test_private_count(self, apiobj):
        """Pass."""
        data = apiobj._count()
        assert isinstance(data, int)

    def test_private_count_query(self, apiobj):
        """Pass."""
        query = QUERIES["not_last_seen_day"]
        data = apiobj._count(query=query)
        assert isinstance(data, int)

    def test_private_build_query(self, apiobj):
        """Pass."""
        pre_query = QUERIES["not_last_seen_day"]
        post_query = QUERIES["not_last_seen_day"]

        inner = 'hostname == "badwolf"'
        pre = f"{pre_query} and"
        post = f"and {post_query}"

        query = apiobj._build_query(inner=inner)
        assert query == f"({inner})"

        query = apiobj._build_query(inner=inner, not_flag=True)
        assert query == f"(not ({inner}))"

        query = apiobj._build_query(inner=inner, pre=pre)
        assert query == f"{pre} ({inner})"

        query = apiobj._build_query(inner=inner, post=post)
        assert query == f"({inner}) {post}"

        query = apiobj._build_query(inner=inner, pre=pre, post=post)
        assert query == f"{pre} ({inner}) {post}"

        query = apiobj._build_query(inner=inner, pre=pre, post=post, not_flag=True)
        assert query == f"{pre} (not ({inner})) {post}"


class AssetsPublic:
    """Pass."""

    def test_count(self, apiobj):
        """Pass."""
        data = apiobj.count()
        assert isinstance(data, int)

    def test_count_query(self, apiobj):
        """Pass."""
        query = QUERIES["not_last_seen_day"]
        data = apiobj.count(query=query)
        assert isinstance(data, int)

    def test_count_by_saved_query(self, apiobj):
        """Pass."""
        sq = apiobj.TEST_DATA["saved_queries"][0]
        sq_name = sq["name"]
        data = apiobj.count_by_saved_query(name=sq_name)
        assert isinstance(data, int)

    def test_get_cursor_no_generator_no(self, apiobj):
        """Pass."""
        rows = apiobj.get(use_cursor=False, generator=False, max_rows=1)

        assert not rows.__class__.__name__ == "generator"
        assert "cached" not in apiobj.auth.http.LAST_RESPONSE.request.url
        check_assets(rows)
        assert len(rows) == 1

    def test_get_cursor_no_generator_yes(self, apiobj):
        """Pass."""
        gen = apiobj.get(use_cursor=False, generator=True, max_rows=1)

        assert not isinstance(gen, list)
        assert gen.__class__.__name__ == "generator"

        rows = [x for x in gen]

        assert "cached" not in apiobj.auth.http.LAST_RESPONSE.request.url
        check_assets(rows)
        assert len(rows) == 1

    def test_get_cursor_yes_generator_no(self, apiobj):
        """Pass."""
        if getattr(apiobj, "NO_CURSOR_OVERRIDE", False):
            pytest.skip(f"{apiobj} has no cursor override")

        rows = apiobj.get(use_cursor=True, generator=False, max_rows=1)

        assert not rows.__class__.__name__ == "generator"
        assert "cached" in apiobj.auth.http.LAST_RESPONSE.request.url
        check_assets(rows)
        assert len(rows) == 1

    def test_get_cursor_yes_generator_yes(self, apiobj):
        """Pass."""
        if getattr(apiobj, "NO_CURSOR_OVERRIDE", False):
            pytest.skip(f"{apiobj} has no cursor override")

        gen = apiobj.get(use_cursor=True, generator=True, max_rows=1)

        assert gen.__class__.__name__ == "generator"

        rows = [x for x in gen]
        assert "cached" in apiobj.auth.http.LAST_RESPONSE.request.url
        check_assets(rows)
        assert len(rows) == 1

    def test_get_page_size_over_max(self, apiobj):
        """Pass."""
        rows = apiobj.get(page_size=3000, max_pages=1)
        check_assets(rows)
        assert len(rows) <= MAX_PAGE_SIZE

    def test_get_maxpages(self, apiobj):
        """Pass."""
        rows = apiobj.get(page_size=20, max_pages=1)
        check_assets(rows)
        assert len(rows) == 20

    def test_get_id(self, apiobj):
        """Pass."""
        asset = apiobj.TEST_DATA["assets"][0]
        id = asset["internal_axon_id"]

        row = apiobj.get_by_id(id=id)
        check_asset(row)
        assert row["internal_axon_id"] == id

    def test_get_id_error(self, apiobj):
        """Pass."""
        with pytest.raises(NotFoundError):
            apiobj.get_by_id(id="badwolf")

    def test_get_by_saved_query(self, apiobj):
        """Pass."""
        sq = apiobj.TEST_DATA["saved_queries"][0]
        sq_name = sq["name"]
        sq_fields = sq["view"]["fields"]

        rows = apiobj.get_by_saved_query(
            name=sq_name, max_rows=1, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        last_fields = apiobj._LAST_GET["fields"].split(",")
        assert sq_fields == last_fields

    def test_get_by_value(self, apiobj):
        """Pass."""
        field = apiobj.TEST_DATA["field_main"]

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_value(
            value=value, field=field, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)
        assert len(rows) == 1

        rows_values = get_field_values(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_value_not(self, apiobj):
        """Pass."""
        field = apiobj.TEST_DATA["field_main"]

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_value(
            value=value,
            field=field,
            not_flag=True,
            fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_values(self, apiobj):
        """Pass."""
        field = apiobj.TEST_DATA["field_main"]

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_values(
            values=values, field=field, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        for value in values:
            assert value in rows_values

    def test_get_by_values_not(self, apiobj):
        """Pass."""
        field = apiobj.TEST_DATA["field_main"]

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_values(
            values=values,
            field=field,
            not_flag=True,
            fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        for value in values:
            assert value not in rows_values

    def test_get_by_value_regex(self, apiobj):
        """Pass."""
        field = apiobj.TEST_DATA["field_main"]

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_value_regex(
            value=regex_value, field=field, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_value_regex_not(self, apiobj):
        """Pass."""
        field = apiobj.TEST_DATA["field_main"]

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_value_regex(
            value=regex_value,
            field=field,
            not_flag=True,
            fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value not in rows_values


def get_field_values(rows, field):
    """Pass."""
    values = [x[field] for x in rows if x.get(field)]
    values = [x for y in values for x in listify(y)]
    return values


def check_assets(rows):
    """Pass."""
    assert isinstance(rows, list)
    for row in rows:
        check_asset(row)


def check_asset(row):
    """Pass."""
    assert isinstance(row, dict)
    assert row["internal_axon_id"]
