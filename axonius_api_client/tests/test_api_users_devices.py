# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import copy

import pytest
import requests

import axonius_api_client as axonapi

CLASSES = [axonapi.api.Users, axonapi.Devices]

LABELS = ["badwolf_dundundun"]

QUERY_SINGLE = '(specific_data.data.id == ({"$exists":true,"$ne": ""}))'
QUERY_MULTI = [None, QUERY_SINGLE]

USERS_FIELDS_MANUAL = ["specific_data.data.username"]
USERS_FIELDS_VAL = ["username"]

DEVICES_FIELDS_MANUAL = ["specific_data.data.hostname"]
DEVICES_FIELDS_VAL = ["hostname"]

GENERIC_FIELDS = {
    "users": {"generic": USERS_FIELDS_VAL},
    "devices": {"generic": DEVICES_FIELDS_VAL},
}

GENERIC_FIELDS_MIX = {
    "users": {"generic": USERS_FIELDS_VAL + USERS_FIELDS_MANUAL},
    "devices": {"generic": DEVICES_FIELDS_VAL + DEVICES_FIELDS_MANUAL},
}


def need_creds(creds):
    """Pass."""
    if not any(list(creds["creds"].values())):
        pytest.skip("No credentials provided for {cls}: {creds}".format(**creds))


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize("creds", ["creds_user", "creds_key"], indirect=True)
@pytest.mark.parametrize("apicls", CLASSES, scope="session")
class TestUserDevices(object):
    """Pass."""

    @pytest.fixture(scope="session")
    def apiobj(self, url, creds, apicls):
        """Pass."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        api = apicls(auth=auth)
        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)
        assert axonapi.tools.is_type.dict(api._default_fields)
        assert isinstance(api._router, axonapi.api.routers.Router)
        assert isinstance(api.labels, axonapi.api.mixins.Child)
        assert isinstance(api.labels, axonapi.api.users_devices.Labels)
        assert isinstance(api.saved_query, axonapi.api.mixins.Child)
        assert isinstance(api.saved_query, axonapi.api.users_devices.SavedQuery)
        assert isinstance(api.fields, axonapi.api.mixins.Child)
        assert isinstance(api.fields, axonapi.api.users_devices.Fields)
        assert isinstance(api.reports, axonapi.api.mixins.Child)
        assert isinstance(api.reports, axonapi.api.users_devices.Reports)
        assert isinstance(api.adapters, axonapi.api.adapters.Adapters)
        return api

    @pytest.fixture(scope="session")
    def single_asset(self, apiobj):
        """Pass."""
        return apiobj._get(page_size=1)["assets"][0]

    @pytest.fixture(scope="session")
    def single_asset_query(self, single_asset):
        """Pass."""
        asset_id = single_asset["internal_axon_id"]
        return 'internal_axon_id == "{}"'.format(asset_id)

    @pytest.fixture(scope="session")
    def api_fields(self, apiobj):
        """Pass."""
        return apiobj.fields.get()

    @pytest.fixture(scope="session")
    def test_sq_get(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get()
        assert axonapi.tools.is_type.lod(data)
        for entry in data:
            assert "name" in entry
            assert axonapi.tools.is_type.str(entry["name"])
        return data

    def test__request_json(self, apiobj):
        """Test that JSON is returned when is_json=True."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=False,
            is_json=True,
            check_status=True,
        )
        assert axonapi.tools.is_type.dict(response)

    def test__request_raw(self, apiobj):
        """Test that response is returned when raw=True."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=True,
            is_json=True,
            check_status=True,
        )
        assert isinstance(response, requests.Response)

    def test__request_text(self, apiobj):
        """Test that str is returned when raw=False and is_json=False."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=False,
            is_json=False,
            check_status=True,
        )
        assert axonapi.tools.is_type.str(response)

    def test_not_logged_in(self, url, creds, apicls):
        """Test exc thrown when auth method not logged in."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        with pytest.raises(axonapi.NotLoggedIn):
            apicls(auth=auth)

    @pytest.mark.parametrize("query", QUERY_MULTI)
    @pytest.mark.parametrize(
        "fields",
        [
            {"users": None, "devices": None},
            {"users": USERS_FIELDS_MANUAL, "devices": DEVICES_FIELDS_MANUAL},
        ],
    )
    @pytest.mark.parametrize("use_post", [True, False])
    @pytest.mark.parametrize("row_start", [0, 1])
    def test__get(self, apiobj, query, fields, use_post, row_start):
        """Test private get."""
        api_type = apiobj._router._object_type
        api_fields = fields[api_type]
        data = apiobj._get(
            fields=api_fields,
            row_start=row_start,
            page_size=1,
            query=query,
            use_post=use_post,
        )
        assert axonapi.tools.is_type.dict(data)
        assert "assets" in data
        assert axonapi.tools.is_type.list(data["assets"])

        if not data["assets"]:
            msg = "No {t} on system, unable to test _get"
            msg = msg.format(t=api_type)
            pytest.skip(msg)

        assert len(data["assets"]) == 1

        for entry in data["assets"]:
            assert axonapi.tools.is_type.dict(entry)
            assert "adapters" in entry
            if api_fields:
                for field in api_fields:
                    assert field in entry
            else:
                assert "specific_data" in entry

    @pytest.mark.parametrize("query", QUERY_MULTI)
    @pytest.mark.parametrize("use_post", [True, False])
    def test_count(self, apiobj, query, use_post):
        """Test count."""
        data = apiobj.count(query=query, use_post=use_post)
        assert axonapi.tools.is_type.int(data)

    @pytest.mark.parametrize(
        "manual_fields",
        [{"users": USERS_FIELDS_MANUAL, "devices": DEVICES_FIELDS_MANUAL}],
    )
    def test_get_manual(self, apiobj, manual_fields, single_asset_query):
        """Pass."""
        api_type = apiobj._router._object_type
        api_manual_fields = manual_fields[api_type]
        data = apiobj.get(query=single_asset_query, manual_fields=api_manual_fields)
        assert axonapi.tools.is_type.list(data)
        assert len(data) == 1

    @pytest.mark.parametrize("val_fields", [GENERIC_FIELDS_MIX])
    def test_get_val(self, apiobj, val_fields, single_asset_query):
        """Pass."""
        api_type = apiobj._router._object_type
        api_manual_fields = copy.deepcopy(val_fields[api_type])
        data = apiobj.get(query=single_asset_query, **api_manual_fields)
        assert axonapi.tools.is_type.list(data)
        assert len(data) == 1

    @pytest.mark.parametrize("query", [None, 'name == regex("a", "i")'])
    @pytest.mark.parametrize("row_start", [0, 1])
    def test_sq__get_direct(self, apiobj, query, row_start):
        """Test sq private get_direct."""
        data = apiobj.saved_query._get_direct(
            query=query, row_start=row_start, page_size=1
        )
        assert axonapi.tools.is_type.dict(data)
        assert "assets" in data
        assert axonapi.tools.is_type.list(data["assets"])
        assert len(data["assets"]) == 1

        for entry in data["assets"]:
            assert axonapi.tools.is_type.dict(entry)
            assert "name" in entry
            assert axonapi.tools.is_type.str(entry["name"])

    def test_sq__get(self, apiobj):
        """Test sq private get."""
        data = apiobj.saved_query._get()
        assert axonapi.tools.is_type.list(data)
        assert len(data) >= 1

        for entry in data:
            assert axonapi.tools.is_type.dict(entry)
            assert "name" in entry
            assert axonapi.tools.is_type.str(entry["name"])

    def test_sq_get_names(self, apiobj):
        """Test sq get_names."""
        data = apiobj.saved_query.get_names()
        assert axonapi.tools.is_type.list(data)
        assert len(data) >= 1

        for entry in data:
            assert axonapi.tools.is_type.str(entry)

    @pytest.mark.parametrize(
        "sort_field",
        [
            {"users": USERS_FIELDS_MANUAL[0], "devices": DEVICES_FIELDS_MANUAL[0]},
            {"users": USERS_FIELDS_VAL[0], "devices": DEVICES_FIELDS_VAL[0]},
            {"users": None, "devices": None},
        ],
    )
    @pytest.mark.parametrize(
        "manual_fields",
        [{"users": USERS_FIELDS_MANUAL, "devices": DEVICES_FIELDS_MANUAL}],
    )
    def test_sq_create_delete_manual(self, sort_field, manual_fields, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type
        api_manual_fields = manual_fields[api_type]
        api_sort_field = sort_field[api_type]
        api_sort_field = api_sort_field

        name = "BADWOLF {}".format(axonapi.tools.dt.now())

        created = apiobj.saved_query.create(
            name=name,
            query=QUERY_SINGLE,
            sort_field=api_sort_field,
            manual_fields=api_manual_fields,
        )
        assert axonapi.tools.is_type.dict(created)
        assert created["name"] == name

        apiobj.saved_query.delete(name=created["name"])

        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.saved_query.get(name=name)

    @pytest.mark.parametrize("fields", [GENERIC_FIELDS, {"users": {}, "devices": {}}])
    def test_sq_create_delete_val(self, fields, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type

        name = "BADWOLF {}".format(axonapi.tools.dt.now())

        created = apiobj.saved_query.create(
            name=name, query=QUERY_SINGLE, **copy.deepcopy(fields[api_type])
        )
        assert axonapi.tools.is_type.dict(created)
        assert created["name"] == name

        apiobj.saved_query.delete(name=created["name"])

        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.saved_query.get(name=name)

    def test_sq_create_page_size_invalid(self, apiobj):
        """Pass."""
        with pytest.raises(axonapi.exceptions.ApiError):
            apiobj.saved_query.create(name="BADWOLF", query=None, page_size=99290)

    def test_sq_get_invalid(self, apiobj):
        """Pass."""
        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.saved_query.get(name="AJKSLDBIBRASNVOIRHOUHG")

    def test_sq_get_name(self, apiobj, test_sq_get):
        """Pass."""
        name = test_sq_get[0]["name"]
        data = apiobj.saved_query.get(name=name)
        assert axonapi.tools.is_type.dict(data)
        assert "name" in data
        assert axonapi.tools.is_type.str(data["name"])

    def test_sq_get_name_re(self, apiobj, test_sq_get):
        """Pass."""
        name = test_sq_get[0]["name"][0]
        data = apiobj.saved_query.get(name=name, regex=True)
        assert axonapi.tools.is_type.lod(data)
        assert len(data) >= 1

    def test_labels_get(self, apiobj):
        """Pass."""
        data = apiobj.labels.get()
        assert axonapi.tools.is_type.list(data)
        for entry in data:
            assert axonapi.tools.is_type.str(entry)

    def test_labels_add(self, single_asset_query, apiobj):
        """Pass."""
        data = apiobj.labels.add(query=single_asset_query, labels=LABELS)
        assert axonapi.tools.is_type.int(data)
        assert data == 1

    def test_labels_add_by_rows(self, single_asset, apiobj):
        """Pass."""
        data = apiobj.labels.add_by_rows(rows=[single_asset], labels=LABELS)
        assert axonapi.tools.is_type.int(data)
        assert data == 1

    def test_labels_delete(self, single_asset_query, apiobj):
        """Pass."""
        data = apiobj.labels.delete(query=single_asset_query, labels=LABELS)
        assert axonapi.tools.is_type.int(data)
        assert data == 1

    def test_labels_delete_by_rows(self, single_asset, apiobj):
        """Pass."""
        data = apiobj.labels.delete_by_rows(rows=[single_asset], labels=LABELS)
        assert axonapi.tools.is_type.int(data)
        assert data == 1

    def test_fields_get(self, api_fields):
        """Pass."""
        assert axonapi.tools.is_type.dict(api_fields)
        assert "generic" in api_fields

    @pytest.mark.parametrize(
        "adapter_name", ["generic", "active_directory"], scope="session"
    )
    def test_fields_find_adapter(self, apiobj, api_fields, adapter_name):
        """Pass."""
        name, obj_fields = apiobj.fields.find_adapter(adapter_name, fields=api_fields)
        assert axonapi.tools.is_type.str(name)
        assert axonapi.tools.is_type.dict(obj_fields)

    def test_fields_find_adapter_invalid(self, apiobj, api_fields):
        """Pass."""
        with pytest.raises(axonapi.exceptions.UnknownError):
            apiobj.fields.find_adapter("badwolf", fields=api_fields)

    @pytest.mark.parametrize("generic_fields", [GENERIC_FIELDS_MIX])
    def test_fields_find(self, apiobj, api_fields, generic_fields):
        """Pass."""
        api_type = apiobj._router._object_type
        api_type_fields = generic_fields[api_type]["generic"]
        for api_type_field in api_type_fields:
            name = apiobj.fields.find(
                adapter_name="generic", name=api_type_field, fields=api_fields
            )
            assert axonapi.tools.is_type.str(name)

    def test_fields_find_invalid_field(self, apiobj, api_fields):
        """Pass."""
        with pytest.raises(axonapi.exceptions.UnknownError):
            apiobj.fields.find(adapter_name="generic", name="AJKSLJAKN")

    def test_fields_find_invalid_adapter(self, apiobj, api_fields):
        """Pass."""
        with pytest.raises(axonapi.exceptions.UnknownError):
            apiobj.fields.find(adapter_name="SDNJS:LDJGSKLDJF", name="AJKSLJAKN")

    def test_fields_validate_ignores(self, apiobj, api_fields):
        """Pass."""
        kwargs = {"x": [None, pytest]}
        data = apiobj.fields.validate(fields=api_fields, default_fields=False, **kwargs)
        assert not data

    @pytest.mark.parametrize("generic_fields", [GENERIC_FIELDS_MIX])
    def test_fields_validate(self, apiobj, api_fields, generic_fields):
        """Pass."""
        api_type = apiobj._router._object_type
        api_type_fields = copy.deepcopy(generic_fields[api_type])
        data = apiobj.fields.validate(
            fields=api_fields, default_fields=False, **api_type_fields
        )
        assert axonapi.tools.is_type.list(data)
        if len(data) != 1:
            import pdb

            pdb.set_trace()
        assert len(data) == 1
        for entry in data:
            assert axonapi.tools.is_type.str(entry)

    @pytest.mark.parametrize("generic_fields", [GENERIC_FIELDS_MIX])
    def test_fields_validate_all(self, apiobj, api_fields, generic_fields):
        """Pass."""
        api_type = apiobj._router._object_type
        api_type_fields = copy.deepcopy(generic_fields[api_type])
        api_type_fields["generic"].append("all")
        data = apiobj.fields.validate(
            fields=api_fields, default_fields=False, **api_type_fields
        )
        assert axonapi.tools.is_type.list(data)
        assert len(data) == 1
        assert data[0] == "specific_data"
        for entry in data:
            assert axonapi.tools.is_type.str(entry)

    # TODO
    # test response error by using invalid route
    # test "error" in json response somehow (need to add code for it too)
    # test invalid json response somehow
