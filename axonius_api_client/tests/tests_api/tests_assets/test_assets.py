# -*- coding: utf-8 -*-
"""Test suite for assets."""
import datetime
from typing import Any, List

import pytest

from axonius_api_client.api import json_api, mixins, AssetMixin

from axonius_api_client.exceptions import ApiError, NotFoundError, StopFetch, ToolsError
from axonius_api_client.tools import listify

from ...meta import QUERIES
from ...utils import FLAKY, check_asset, check_assets


class WizData:
    """Pass."""

    wiz_str: str = "simple active_directory:id exists"
    wiz_dict: dict = {"type": "simple", "value": "active_directory:id exists"}
    exp: dict = {
        "expressions": [
            {
                "bracketWeight": 0,
                "children": [
                    {
                        "condition": "",
                        "expression": {
                            "compOp": "",
                            "field": "",
                            "filteredAdapters": None,
                            "value": None,
                        },
                        "i": 0,
                    }
                ],
                "compOp": "exists",
                "field": "adapters_data.active_directory_adapter.id",
                "fieldType": "active_directory_adapter",
                "filter": '(("adapters_data.active_directory_adapter.id" == '
                '({"$exists":true,"$ne":""})))',
                "filteredAdapters": None,
                "leftBracket": False,
                "logicOp": "",
                "not": False,
                "rightBracket": False,
                "value": None,
            }
        ],
        "query": '(("adapters_data.active_directory_adapter.id" == '
        '({"$exists":true,"$ne":""})))',
    }
    invalids: List[Any] = [1, [[]]]
    nones: List[Any] = [[], None, {}, ""]


class ModelMixinsBase:
    """Pass."""

    @staticmethod
    def test_model_child(apiobj):
        child = mixins.ChildMixins(parent=apiobj)
        assert str(apiobj) in str(child)
        assert repr(apiobj) in repr(child)


@pytest.mark.slow
@pytest.mark.trylast
class TestAssetsPrivate(ModelMixinsBase):
    """Pass."""

    @pytest.fixture(params=["api_devices"], scope="class")
    def apiobj(self, request):
        """Pass."""
        return request.getfixturevalue(request.param)

    def test_history_dates(self, apiobj):
        def check_asset_type_history_date(obj):
            """Pass."""
            assert isinstance(obj, json_api.assets.AssetTypeHistoryDate)
            assert str(obj)
            assert repr(obj)

        def check_asset_type_history_dates(obj):
            """Pass."""
            assert isinstance(obj, json_api.assets.AssetTypeHistoryDates)
            assert str(obj)
            assert repr(obj)
            assert isinstance(obj.dates, list)
            assert obj.get_date() is None

            if not obj.dates:
                return

            for date in obj.dates:
                check_asset_type_history_date(date)

            for days, date in obj.dates_by_days_ago.items():
                assert isinstance(days, int)
                assert isinstance(date, json_api.assets.AssetTypeHistoryDate)

            date_oldest = sorted(obj.dates, key=lambda x: x.date)[0]

            with pytest.raises(ToolsError):
                obj.get_date_by_days_ago(value="xxx")

            date = obj.get_date_by_days_ago(value="0")
            assert isinstance(date, str) and date

            date = obj.get_date_by_days_ago(value=0)
            assert isinstance(date, str) and date

            date = obj.get_date_by_days_ago(value=999, exact=False)
            assert isinstance(date, str) and date
            assert date == date_oldest.date_api_exact

            with pytest.raises(ApiError):
                obj.get_date_by_days_ago(value=999, exact=True)

            value = datetime.datetime.utcnow() - datetime.timedelta(days=999)
            date = obj.get_date_nearest(value=value)
            assert date == date_oldest

            date = obj.get_date_by_date(value=date_oldest.date_api, exact=True)
            assert date == date_oldest.date_api_exact

            with pytest.raises(ApiError):
                obj.get_date_by_date(value="1999-01-01", exact=True)

            with pytest.raises(ApiError):
                obj.get_date_by_date(value="xxx", exact=True)

            date = obj.get_date_by_date(value="1999-01-01", exact=False)
            assert date == date_oldest.date_api_exact
            # with pytest.raises(ApiError):
            #     obj.get_date(date="1999-01-01")

        data = apiobj._history_dates()
        assert str(data)
        assert repr(data)
        assert isinstance(data, json_api.assets.HistoryDates)
        assert isinstance(data.parsed, dict) and data.parsed
        for asset_type, dates in data.parsed.items():
            assert isinstance(asset_type, str)
            assert asset_type in data.value
            check_asset_type_history_dates(dates)

    def test_get_asset_page(self, apiobj, monkeypatch):
        def check_page(page):
            """Pass."""
            state = page.create_state()
            assert isinstance(state, dict)
            assert isinstance(page, json_api.assets.AssetsPage)
            assert isinstance(page.assets, list)
            if page.asset_count_total:
                assert len(page.assets) == 1
                assert page.asset_count_page == 1
                assert page.pages_total >= 1
            assert isinstance(page.cursor, str) and page.cursor
            assert isinstance(page.page, dict) and page.page
            assert isinstance(page.pages_total, int)

        page1 = apiobj._get(offset=0, limit=1)
        check_page(page1)

        page2 = apiobj._get(offset=1, limit=1, cursor_id=page1.cursor)
        check_page(page2)

        page3 = apiobj._get(offset=2, limit=1, cursor_id=page1.cursor)
        state1 = page1.create_state()
        if page1.asset_count_total:
            assert page1.page_number == 1
            assert page2.page_number == 2
            assert page3.page_number == 3

            state1_max_rows = page1.create_state(max_rows=2)
            assert state1_max_rows["page_size"] == 2

            state1_page_start = page1.create_state(page_start=2, page_size=2)
            assert state1_page_start["rows_offset"] == 4

            page2.process_page(state=state1, start_dt=page1.page_start_dt, apiobj=apiobj)
            assert state1["page_number"] == 2
            page2.process_row(state=state1, apiobj=apiobj, row=page2.assets[0])
            page2.process_loop(state=state1, apiobj=apiobj)
            assert state1["page_loop"] == 2

        with monkeypatch.context() as m:
            m.setattr(page3, "assets", [])
            with pytest.raises(StopFetch):
                page3.process_page(state={**state1}, start_dt=page1.page_start_dt, apiobj=apiobj)

    @pytest.mark.skip("BREAKER: induces timeout")
    def test_get_pages(self, apiobj):
        page1 = apiobj._get(offset=0, limit=5)
        cursor = page1.cursor
        page2 = apiobj._get(offset=5, limit=5, cursor_id=cursor)
        page3 = apiobj._get(offset=10, limit=5, cursor_id=cursor)
        if page1.asset_count_total:
            assert len(page1.assets) == 5
            assert len(page2.assets) == 5
            assert len(page3.assets) == 5
            assert len(page1.assets + page2.assets + page3.assets) == 15

    @pytest.mark.parametrize("value", WizData.nones)
    def test_get_wiz_entries_none(self, apiobj, value):
        data = apiobj.get_wiz_entries(wiz_entries=value)
        assert data is None

    @pytest.mark.parametrize("value", WizData.invalids)
    def test_get_wiz_entries_wrong_type(self, apiobj, value):
        with pytest.raises(ApiError):
            apiobj.get_wiz_entries(wiz_entries=value)

    def test_get_wiz_entries_text(self, apiobj):
        data = apiobj.get_wiz_entries(wiz_entries=WizData.wiz_str)
        assert data == WizData.exp

    def test_get_wiz_entries_dict(self, apiobj):
        data = apiobj.get_wiz_entries(wiz_entries=WizData.wiz_dict)
        assert data == WizData.exp

    def test_get_query(self, apiobj):
        query = QUERIES["not_last_seen_day"]
        data = apiobj._get(filter=query, limit=1)
        assert isinstance(data, json_api.assets.AssetsPage)
        assert isinstance(data.assets, list)
        assert len(data.assets) == 1

    def test_get_by_id_dc(self, apiobj):
        ax_id = apiobj.ORIGINAL_ROWS[0]["internal_axon_id"]
        data = apiobj._get_by_id(id=ax_id)
        assert isinstance(data, json_api.assets.AssetById)
        assert data.id == ax_id

    def test_count_dc(self, apiobj):
        data = apiobj._count()
        assert isinstance(data, json_api.assets.Count)
        assert isinstance(data.value, int)

    def test_count_query(self, apiobj):
        query = QUERIES["not_last_seen_day"]
        data = apiobj._count(filter=query)
        assert isinstance(data, json_api.assets.Count)
        assert isinstance(data.value, int)

    def test_build_query(self, apiobj):
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


class TestAssetsPublic(ModelMixinsBase):
    @pytest.fixture(params=["api_devices"], scope="class")
    def apiobj(self, request):
        """Pass."""
        return request.getfixturevalue(request.param)

    def test_cls_asset_modules(self, apiobj):
        data = apiobj.asset_modules()
        assert isinstance(data, list) and data
        for item in data:
            assert issubclass(item, AssetMixin)

    def test_cls_asset_types(self, apiobj):
        data = apiobj.asset_types()
        assert isinstance(data, list) and data
        for item in data:
            assert isinstance(item, str)

    @FLAKY()
    def test_sort(self, apiobj):
        apiobj.get(max_rows=1, sort_field=apiobj.FIELD_MAIN, http_args={"response_timeout": 30})

    def test_sort_bad(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get(max_rows=1, sort_field="badwolf")

    def test_history_date(self, apiobj):
        data = apiobj.history_dates()
        assert isinstance(data, dict)
        for short, full in data.items():
            assert isinstance(short, str) and "-" in short
            assert isinstance(full, str) and "-" in full and "T" in full

    def test_count(self, apiobj):
        data = apiobj.count()
        assert isinstance(data, int)

    def test_count_query(self, apiobj):
        query = QUERIES["not_last_seen_day"]
        data = apiobj.count(query=query)
        assert isinstance(data, int)

    def test_count_wiz(self, apiobj):
        data = apiobj.count(wiz_entries="simple active_directory:id exists")
        assert isinstance(data, int)

    def test_count_by_saved_query(self, apiobj):
        sq_name = apiobj.saved_query.get()[0]["name"]
        data = apiobj.count_by_saved_query(name=sq_name)
        assert isinstance(data, int)

    @FLAKY()
    def test_get_agg_raw_data(self, apiobj):
        rows = apiobj.get(max_rows=1, fields=["agg:raw_data"], http_args={"response_timeout": 30})
        for row in rows:
            self.validate_raw_data(apiobj=apiobj, row=row, field="specific_data.data.raw_data")

    @staticmethod
    def validate_raw_data(apiobj, row, field):
        """Pass."""
        adapters = row["adapters"]
        raw_datas = row.get(field)
        assert isinstance(raw_datas, (dict, list)) and raw_datas

        raw_datas = listify(raw_datas)
        for raw_data in raw_datas:
            assert isinstance(raw_data["data"], dict)
            assert isinstance(raw_data["plugin_name"], str) and raw_data["plugin_name"]
            assert isinstance(raw_data["client_used"], str) and raw_data["client_used"]
            assert raw_data["plugin_name"] in adapters

    @FLAKY()
    def test_get_adapter_raw_data(self, apiobj):
        field = "adapters_data.active_directory_adapter.raw_data"
        fields = ["active_directory:raw_data"]
        wiz = "simple active_directory:id exists"
        http_args = {"response_timeout": 30}

        rows = apiobj.get(max_rows=1, fields=fields, wiz_entries=wiz, http_args=http_args)
        for row in rows:
            self.validate_raw_data(apiobj=apiobj, row=row, field=field)

    @FLAKY()
    def test_get_all_agg(self, apiobj):
        rows = apiobj.get(fields="agg:all", max_rows=1, http_args={"response_timeout": 30})
        for row in rows:
            assert "specific_data" in row
            all_datas = row["specific_data"]
            assert isinstance(all_datas, list)
            for all_data in all_datas:
                assert isinstance(all_data, dict)
                assert isinstance(all_data["plugin_name"], str) and all_data["plugin_name"]
                assert (
                    isinstance(all_data["accurate_for_datetime"], str)
                    and all_data["accurate_for_datetime"]
                )

                if all_data["plugin_name"] not in ["static_analysis", "gui"]:
                    assert isinstance(all_data["client_used"], str) and all_data["client_used"]

    @FLAKY()
    def test_get_all_adapter(self, apiobj):
        rows = apiobj.get(
            fields="active_directory:all",
            wiz_entries="simple active_directory:id exists",
            max_rows=1,
            http_args={"response_timeout": 30},
        )
        for row in rows:
            assert "adapters_data.active_directory_adapter" in row
            all_datas = row["adapters_data.active_directory_adapter"]
            assert isinstance(all_datas, list)
            for all_data in all_datas:
                assert isinstance(all_data, dict)
                assert (
                    isinstance(all_data["accurate_for_datetime"], str)
                    and all_data["accurate_for_datetime"]
                )

    @FLAKY()
    def test_get_id(self, apiobj):
        axon_id = apiobj.ORIGINAL_ROWS[0]["internal_axon_id"]

        row = apiobj.get_by_id(id=axon_id)
        check_asset(row)
        assert row["internal_axon_id"] == axon_id

    def test_get_id_error(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_by_id(id="badwolf")

    @FLAKY()
    def test_get_by_saved_query(self, apiobj):
        sq = apiobj.saved_query.get()[0]
        sq_name = sq["name"]
        sq_fields = sq["view"]["fields"]

        rows = apiobj.get_by_saved_query(
            name=sq_name, max_rows=1, http_args={"response_timeout": 30}
        )
        check_assets(rows)

        last_fields = apiobj.LAST_GET["fields"][apiobj.ASSET_TYPE]
        assert sq_fields == last_fields
