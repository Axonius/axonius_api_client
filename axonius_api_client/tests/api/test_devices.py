# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import requests
import six

import axonius_api_client


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize("creds", ["creds_user", "creds_key"], indirect=True)
class TestDevices(object):
    """Test axonius_api_client.api.Devices."""

    @pytest.fixture(scope="session")
    def api_client(self, api_url, creds):
        """Get an API client."""
        auth_cls = creds["cls"]
        creds = {k: v for k, v in creds.items() if k != "cls"}
        if not any(list(creds.values())):
            pytest.skip("No credentials provided for {}: {}".format(auth_cls, creds))
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = auth_cls(http_client=http_client, **creds)
        auth.login()
        api_client = axonius_api_client.api.Devices(auth=auth)
        return api_client

    def test__request_json(self, api_client):
        """Test that JSON is returned when is_json=True."""
        response = api_client._request(
            path=axonius_api_client.api.routers.ApiV1.devices.count,
            method="get",
            raw=False,
            is_json=True,
            check_status=True,
        )
        assert not isinstance(response, requests.Response)
        assert not isinstance(response, six.string_types)

    def test__request_raw(self, api_client):
        """Test that response obj is returned when raw=True."""
        response = api_client._request(
            path=axonius_api_client.api.routers.ApiV1.devices.count,
            method="get",
            raw=True,
            is_json=True,
            check_status=True,
        )
        assert isinstance(response, requests.Response)

    def test__request_text(self, api_client):
        """Test that str is returned when raw=False and is_json=False."""
        response = api_client._request(
            path=axonius_api_client.api.routers.ApiV1.devices.count,
            method="get",
            raw=False,
            is_json=False,
            check_status=True,
        )
        assert isinstance(response, six.string_types)

    def test_not_logged_in(self, api_url, creds):
        """Test exc thrown when auth method not logged in."""
        auth_cls = creds["cls"]
        creds = {k: v for k, v in creds.items() if k != "cls"}
        if not any(list(creds.values())):
            pytest.skip("No credentials provided for {}: {}".format(auth_cls, creds))
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = auth_cls(http_client=http_client, **creds)
        with pytest.raises(axonius_api_client.auth.exceptions.NotLoggedIn):
            axonius_api_client.api.Devices(auth=auth)

    # TODO: better _request exc tests
    def test__request_invalid(self, api_client):
        """Test private _request method throws ResponseError."""
        with pytest.raises(axonius_api_client.api.exceptions.ResponseError):
            api_client._request(path="invalid_route")

    def test_str_repr(self, api_client):
        """Test str/repr has URL."""
        assert "auth" in format(api_client)
        assert "auth" in repr(api_client)

    def test_get_fields(self, api_client):
        """Test devices/fields API call."""
        fields = api_client.get_fields()
        assert isinstance(fields, dict)
        assert "specific" in fields
        assert "generic" in fields
        assert "schema" in fields

    def test__get_no_query_no_fields(self, api_client):
        """Test private get method without query or fields."""
        rows = api_client._get(query=None, fields=None, row_start=0, page_size=1)
        assert "assets" in rows
        for row in rows["assets"]:
            assert "adapters" in row
            assert "specific_data" in row

    @pytest.mark.parametrize(
        "fields",
        [
            [
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
            ],
            "specific_data.data.hostname,specific_data.data.network_interfaces.ips",
        ],
    )
    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    def test__get_queries_fields(self, api_client, query, fields):
        """Test private get method with queries and fields."""
        rows = api_client._get(query=query, fields=fields, row_start=0, page_size=1)
        assert "assets" in rows
        for row in rows["assets"]:
            assert "adapters" in row
            assert "internal_axon_id" in row
            assert "specific_data.data.hostname" in row
            assert "specific_data.data.network_interfaces.ips" in row

    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    def test_get_no_fields(self, api_client, query):
        """Test get method with default fields."""
        for row in api_client.get(query=query, page_size=1, page_count=4):
            assert "specific_data.data.hostname" in row
            assert "specific_data.data.network_interfaces.ips" in row

    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    @pytest.mark.parametrize("generic_fields", [["all"], ["specific_data.data"]])
    def test_get_all_fields(self, api_client, query, generic_fields):
        """Test get method with all fields."""
        for row in api_client.get(
            query=query, page_size=2, page_count=1, generic=generic_fields
        ):
            for data in row["specific_data.data"]:
                assert isinstance(data, tuple([dict] + list(six.string_types)))
                assert data

    def test_get_by_name_valid(self, api_client):
        """Test get_by_name with a valid host name."""
        rows = list(api_client.get(page_count=1, page_size=1))
        if not rows:
            msg = "No devices on system, unable to test"
            pytest.skip(msg)

        name = rows[0]["specific_data.data.hostname"]
        name = name[0] if isinstance(name, (list, tuple)) else name
        row = api_client.get_by_name(value=name)
        assert isinstance(row, dict)

    def test_get_by_name_valid_regex(self, api_client):
        """Test get_by_name with a valid host name."""
        rows = list(api_client.get(page_count=1, page_size=1))
        if not rows:
            msg = "No devices on system, unable to test"
            pytest.skip(msg)

        name = rows[0]["specific_data.data.hostname"]
        name = name[0] if isinstance(name, (list, tuple)) else name
        row = api_client.get_by_name(value=name, regex=True)
        assert isinstance(row, dict)

    def test_get_by_name_invalid(self, api_client):
        """Test get_by_name with a valid host name."""
        with pytest.raises(axonius_api_client.api.exceptions.ObjectNotFound):
            api_client.get_by_name(value="this_should_not_exist_yo")

    def test_get_min_max_1_notfound(self, api_client):
        """Test get_by_name with a valid host name."""
        with pytest.raises(axonius_api_client.api.exceptions.ObjectNotFound):
            list(api_client.get(row_count_min=1, row_count_max=1))

    def test_get_min_toofew(self, api_client):
        """Test get_by_name with a valid host name."""
        with pytest.raises(axonius_api_client.api.exceptions.TooFewObjectsFound):
            list(api_client.get(row_count_min=9999999999))

    def test_get_min_toomany(self, api_client):
        """Test get_by_name with a valid host name."""
        with pytest.raises(axonius_api_client.api.exceptions.TooManyObjectsFound):
            list(api_client.get(row_count_max=0))

    def test_get_by_id_valid(self, api_client):
        """Test get_by_id with a valid row id."""
        rows = api_client._get(page_size=1)
        for row in rows["assets"]:
            full_row = api_client.get_by_id(id=row["internal_axon_id"])
            assert "generic" in full_row
            assert "specific" in full_row

    def test_get_by_id_invalid(self, api_client):
        """Test get_by_id with an invalid row id."""
        with pytest.raises(axonius_api_client.api.exceptions.ObjectNotFound):
            api_client.get_by_id(id="this_wont_work_yo")

    def test_get_count(self, api_client):
        """Test devices/count API call."""
        response = api_client.get_count()
        assert isinstance(response, six.integer_types)

    def test_get_count_query(self, api_client):
        """Test devices/count API call with query (unable to assume greater than 0)."""
        response = api_client.get_count(
            query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))'
        )
        assert isinstance(response, six.integer_types)

    def test_get_count_query_0(self, api_client):
        """Test devices/count API call with query that should return 0."""
        response = api_client.get_count(
            query='(specific_data.data.id == ({"$exists":false,"$eq": "dsaf"}))'
        )
        assert response == 0

    def test__get_saved_query(self, api_client):
        """Test private get_saved_query."""
        rows = api_client._get_saved_query()
        assert isinstance(rows, dict)
        assert "assets" in rows
        assert "page" in rows

    def test_get_saved_query_by_name_invalid(self, api_client):
        """Test get_saved_query_by_name."""
        with pytest.raises(axonius_api_client.api.exceptions.ObjectNotFound):
            api_client.get_saved_query_by_name(name="this_wont_exist_yo", regex=False)

    @pytest.fixture
    def test_create_saved_query_badwolf123(self, api_client):
        """Test create_saved_query."""
        name = "badwolf 123"
        response = api_client.create_saved_query(
            name=name, query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))'
        )
        assert isinstance(response, six.string_types)
        return name, response

    @pytest.fixture
    def test_create_saved_query_badwolf456(self, api_client):
        """Test create_saved_query."""
        name = "badwolf 456"
        response = api_client.create_saved_query(
            name=name,
            query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))',
            sort_field="id",
        )
        assert isinstance(response, six.string_types)
        return name, response

    def test_get_saved_query_by_name_valid(
        self, api_client, test_create_saved_query_badwolf123
    ):
        """Test get_saved_query_by_name."""
        name, id = test_create_saved_query_badwolf123
        rows = api_client.get_saved_query_by_name(name=name, regex=True)
        assert isinstance(rows, (list, tuple))
        assert len(rows) > 0
        for row in rows:
            assert "name" in row
            assert "uuid" in row

    @pytest.mark.parametrize("query", [None, 'name == regex("badwolf", "i")'])
    def test_get_saved_query(
        self, api_client, query, test_create_saved_query_badwolf123
    ):
        """Test get_saved_query."""
        rows = list(api_client.get_saved_query(query=query, page_size=1))
        assert isinstance(rows, (list, tuple))
        assert len(rows) > 0
        for row in rows:
            assert "name" in row
            assert "uuid" in row

    def test_delete_saved_query_by_name(
        self, api_client, test_create_saved_query_badwolf123
    ):
        """Test delete_saved_query_by_name."""
        name, id = test_create_saved_query_badwolf123
        rows = api_client.delete_saved_query_by_name(name=name)
        assert not rows

    def test__delete_saved_query(self, api_client, test_create_saved_query_badwolf456):
        """Test private _delete_saved_query."""
        name, id = test_create_saved_query_badwolf456
        rows = api_client._delete_saved_query(ids=[id])
        assert not rows
