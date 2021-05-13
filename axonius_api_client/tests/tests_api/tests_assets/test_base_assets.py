# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest

from axonius_api_client.api import json_api, mixins
from axonius_api_client.constants.api import MAX_PAGE_SIZE
from axonius_api_client.exceptions import NotFoundError

from ...meta import QUERIES
from ...utils import check_asset, check_assets


class ModelMixinsBase:
    def test_model_child(self, apiobj):
        child = mixins.ChildMixins(parent=apiobj)
        assert str(apiobj) in str(child)
        assert repr(apiobj) in repr(child)


class AssetsPrivate:
    def test_private_get(self, apiobj):
        data = apiobj._get(limit=1)
        assert isinstance(data, json_api.assets.AssetsPage)
        assert isinstance(data.assets, list)
        assert len(data.assets) == 1
        assert data.asset_count_page == 1

    def test_private_get_pages(self, apiobj):
        data1 = apiobj._get(offset=0, limit=5)
        assert len(data1.assets) == 5

        cursor = data1.cursor

        data2 = apiobj._get(offset=5, limit=5, cursor_id=cursor)
        assert len(data2.assets) == 5

        data3 = apiobj._get(offset=10, limit=5, cursor_id=cursor)
        assert len(data3.assets) == 5

        assert len(data1.assets + data2.assets + data3.assets) == 15

    # PBUG: never responds???
    # def test_private_get_pages_no_cursor(self, apiobj):
    #     data1 = apiobj._get(offset=0, limit=5, use_cursor=False, use_cache_entry=True)
    #     assert len(data1.assets) == 5

    #     data2 = apiobj._get(offset=5, limit=5, use_cursor=False, use_cache_entry=True)
    #     assert len(data2.assets) == 5

    #     data3 = apiobj._get(offset=10, limit=5, use_cursor=False, use_cache_entry=True)
    #     assert len(data3.assets) == 5

    #     assert len(data1.assets + data2.assets + data3.assets) == 15

    def test_private_get_query(self, apiobj):
        query = QUERIES["not_last_seen_day"]
        data = apiobj._get(filter=query, limit=1)
        assert isinstance(data, json_api.assets.AssetsPage)
        assert isinstance(data.assets, list)
        assert len(data.assets) == 1

    def test_private_get_by_id(self, apiobj):
        data = apiobj._get(limit=1)
        id = data.assets[0]["internal_axon_id"]
        data = apiobj._get_by_id(id=id)
        assert isinstance(data, json_api.assets.AssetById)
        assert data.id == id

    def test_private_count(self, apiobj):
        data = apiobj._count()
        assert isinstance(data, json_api.assets.Count)
        assert isinstance(data.value, int)

    def test_private_count_query(self, apiobj):
        query = QUERIES["not_last_seen_day"]
        data = apiobj._count(filter=query)
        assert isinstance(data, json_api.assets.Count)
        assert isinstance(data.value, int)

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

    def test_count_by_saved_query(self, apiobj):
        sq_name = apiobj.saved_query.get()[0]["name"]
        data = apiobj.count_by_saved_query(name=sq_name)
        assert isinstance(data, int)

    def test_get_generator_no(self, apiobj):
        rows = apiobj.get(generator=False, max_rows=1)

        assert not rows.__class__.__name__ == "generator"
        check_assets(rows)
        assert len(rows) == 1

    def test_get_generator_yes(self, apiobj):
        gen = apiobj.get(generator=True, max_rows=1)

        assert gen.__class__.__name__ == "generator"

        rows = [x for x in gen]
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

        last_fields = apiobj.LAST_GET["fields"][apiobj.ASSET_TYPE]
        assert sq_fields == last_fields
