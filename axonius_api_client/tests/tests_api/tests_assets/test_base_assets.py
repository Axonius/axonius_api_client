# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest
import requests
from axonius_api_client.api import mixins
from axonius_api_client.constants.api import MAX_PAGE_SIZE
from axonius_api_client.exceptions import (ApiError, JsonError, JsonInvalid,
                                           NotFoundError, ResponseNotOk,
                                           ToolsError)

from ...meta import QUERIES
from ...utils import check_asset, check_assets, get_field_vals, get_rows_exist


class ModelMixinsBase:
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
            apiobj.request(path=apiobj.router.root + "/badwolf", method="get", error_status=False)

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
        child = mixins.ChildMixins(parent=apiobj)
        assert str(apiobj) in str(child)
        assert repr(apiobj) in repr(child)


class AssetsPrivate:
    def test_private_get(self, apiobj):
        data = apiobj._get(page_size=1)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], list)
        assert len(data["assets"]) == 1

    def test_private_get_normal_query(self, apiobj):
        data = apiobj._get(query=QUERIES["not_last_seen_day"], page_size=1)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], list)
        assert len(data["assets"]) == 1

    def test_private_get_cursor(self, apiobj):
        data = apiobj._get_cursor(page_size=1)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], list)
        assert len(data["assets"]) == 1

    def test_private_get_cursor_query(self, apiobj):
        query = QUERIES["not_last_seen_day"]
        data = apiobj._get_cursor(query=query, page_size=1)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], list)
        assert len(data["assets"]) == 1

    def test_private_get_by_id(self, apiobj):
        asset = apiobj.get(max_rows=1)[0]
        id = asset["internal_axon_id"]
        data = apiobj._get_by_id(id=id)
        assert isinstance(data, dict)
        assert data["internal_axon_id"] == id

    def test_private_count(self, apiobj):
        data = apiobj._count()
        assert isinstance(data, int)

    def test_private_count_query(self, apiobj):
        query = QUERIES["not_last_seen_day"]
        data = apiobj._count(query=query)
        assert isinstance(data, int)

    def test_private_build_query(self, apiobj):
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
    def test_sort(self, apiobj):
        apiobj.get(max_rows=1, sort_field=apiobj.FIELD_MAIN)

    def test_sort_bad(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get(max_rows=1, sort_field="badwolf")

    def test_history_date(self, apiobj):
        dates = apiobj.history_dates()
        assert isinstance(dates, dict) and dates
        for k, v in dates.items():
            assert isinstance(k, str) and "-" in k
            assert isinstance(v, str) and "-" in v and "T" in v

    def test_validate_history_date(self, apiobj):
        dates = apiobj.history_dates()
        date = list(dates)[0]
        dt = apiobj.validate_history_date(value=date)
        assert dt == dates[date]

    def test_validate_history_date_unknown_date(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.validate_history_date(value="1999-09-09")

    def test_validate_history_date_invalid_date(self, apiobj):
        with pytest.raises(ToolsError):
            apiobj.validate_history_date(value="xxx")

    def test_count(self, apiobj):
        data = apiobj.count()
        assert isinstance(data, int)

    def test_count_query(self, apiobj):
        query = QUERIES["not_last_seen_day"]
        data = apiobj.count(query=query)
        assert isinstance(data, int)

    def test_count_by_saved_query(self, apiobj):
        sq_name = apiobj.saved_query.get()[0]["name"]
        data = apiobj.count_by_saved_query(name=sq_name)
        assert isinstance(data, int)

    def test_get_cursor_no_generator_no(self, apiobj):
        rows = apiobj.get(use_cursor=False, generator=False, max_rows=1)

        assert not rows.__class__.__name__ == "generator"
        assert "cached" not in apiobj.auth.http.LAST_RESPONSE.request.url
        check_assets(rows)
        assert len(rows) == 1

    def test_get_cursor_no_generator_yes(self, apiobj):
        gen = apiobj.get(use_cursor=False, generator=True, max_rows=1)

        assert not isinstance(gen, list)
        assert gen.__class__.__name__ == "generator"

        rows = [x for x in gen]

        assert "cached" not in apiobj.auth.http.LAST_RESPONSE.request.url
        check_assets(rows)
        assert len(rows) == 1

    def test_get_cursor_yes_generator_no(self, apiobj):
        rows = apiobj.get(use_cursor=True, generator=False, max_rows=1)

        assert not rows.__class__.__name__ == "generator"
        assert "cached" in apiobj.auth.http.LAST_RESPONSE.request.url
        check_assets(rows)
        assert len(rows) == 1

    def test_get_cursor_yes_generator_yes(self, apiobj):
        gen = apiobj.get(use_cursor=True, generator=True, max_rows=1)

        assert gen.__class__.__name__ == "generator"

        rows = [x for x in gen]
        assert "cached" in apiobj.auth.http.LAST_RESPONSE.request.url
        check_assets(rows)
        assert len(rows) == 1

    def test_get_page_size_over_max(self, apiobj):
        rows = apiobj.get(page_size=3000, max_pages=1)
        check_assets(rows)
        assert len(rows) <= MAX_PAGE_SIZE

    def test_get_maxpages(self, apiobj):
        rows = apiobj.get(page_size=20, max_pages=1)
        check_assets(rows)
        assert len(rows) == 20

    def test_get_id(self, apiobj):
        asset = apiobj.get(max_rows=1)[0]
        id = asset["internal_axon_id"]

        row = apiobj.get_by_id(id=id)
        check_asset(row)
        assert row["internal_axon_id"] == id

    def test_get_id_error(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_by_id(id="badwolf")

    def test_get_by_saved_query(self, apiobj):
        sq = apiobj.saved_query.get()[0]
        sq_name = sq["name"]
        sq_fields = sq["view"]["fields"]

        rows = apiobj.get_by_saved_query(name=sq_name, max_rows=1)
        check_assets(rows)

        last_fields = apiobj.LAST_GET["fields"].split(",")
        assert sq_fields == last_fields

    def test_get_bys_value(self, apiobj):
        self._all_get_by(
            apiobj=apiobj,
            method="value",
            field="FIELD_MAIN",
            use_field=apiobj.FIELD_MAIN,
        )

    def _get_by_value(self, apiobj, method, field, not_flag=False, use_field=None):
        field = getattr(apiobj, field)
        row_with_val = get_rows_exist(apiobj=apiobj, fields=field)
        value = get_field_vals(rows=row_with_val, field=field)[0]
        method = getattr(apiobj, f"get_by_{method}")

        method_args = {"value": value, "not_flag": not_flag, "max_rows": 5}
        if use_field:
            method_args["field"] = use_field

        rows = method(**method_args)

        check_assets(rows)
        rows_values = get_field_vals(rows=rows, field=field)

        if not_flag:
            assert value not in rows_values
        else:
            assert len(rows) >= 1
            assert value in rows_values

    def _get_by_values(self, apiobj, method, field, not_flag=False, use_field=None):
        field = getattr(apiobj, field)
        rows_with_val = get_rows_exist(apiobj=apiobj, fields=field, max_rows=2)
        values = get_field_vals(rows=rows_with_val, field=field)
        method = getattr(apiobj, f"get_by_{method}s")

        method_args = {"values": values, "not_flag": not_flag, "max_rows": 5}
        if use_field:
            method_args["field"] = use_field

        rows = method(**method_args)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        for value in values:
            if not_flag:
                assert value not in rows_values
            else:
                assert value in rows_values
                assert len(rows) >= 1

    def _get_by_value_re(self, apiobj, method, field, not_flag=False, use_field=None):
        field = getattr(apiobj, field)
        row_with_val = get_rows_exist(apiobj=apiobj, fields=field)
        value = get_field_vals(rows=row_with_val, field=field)[0]
        regex_value = value[0:5]

        method = getattr(apiobj, f"get_by_{method}_regex")
        method_args = {"value": regex_value, "not_flag": not_flag, "max_rows": 5}
        if use_field:
            method_args["field"] = use_field

        rows = method(**method_args)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        if not_flag:
            assert value not in rows_values
        else:
            assert value in rows_values
            assert len(rows) >= 1

    def _all_get_by(self, apiobj, method, field, use_field=None):
        self._get_by_value(
            apiobj=apiobj,
            method=method,
            field=field,
            not_flag=False,
            use_field=use_field,
        )
        self._get_by_value(
            apiobj=apiobj, method=method, field=field, not_flag=True, use_field=use_field
        )
        self._get_by_values(
            apiobj=apiobj,
            method=method,
            field=field,
            not_flag=False,
            use_field=use_field,
        )
        self._get_by_values(
            apiobj=apiobj, method=method, field=field, not_flag=True, use_field=use_field
        )
        self._get_by_value_re(
            apiobj=apiobj,
            method=method,
            field=field,
            not_flag=False,
            use_field=use_field,
        )
        self._get_by_value_re(
            apiobj=apiobj, method=method, field=field, not_flag=True, use_field=use_field
        )
