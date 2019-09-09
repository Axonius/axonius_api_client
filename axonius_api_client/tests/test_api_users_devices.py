# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pdb  # noqa
import re

import pytest

import axonius_api_client as axonapi
from axonius_api_client import constants, exceptions, tools

from . import utils

FIELD_FORMATS = ["discrete", "image", "date-time", "table", "ip", "subnet", "version"]
SCHEMA_FIELD_FORMATS = [
    "image",
    "date-time",
    "table",
    "logo",
    "tag",
    "ip",
    "subnet",
    "version",
]
FIELD_TYPES = ["string", "bool", "array", "integer", "number"]

QUERY_ID = '(internal_axon_id == "{internal_axon_id}")'.format
QUERY_ID_EXISTS = '(specific_data.data.id == ({"$exists":true,"$ne": ""}))'

# QUERY_TMPL = '({} == ({{"$exists":true,"$ne": ""}}))'.format

# macs = ["00:11:22:33:44:55"] * 10000
# macs = " ".join(["'{}'".format(mac) for mac in macs])
# LONG_QUERY = "not specific_data.data.network_interfaces.mac in [{}]".format(macs)

USERS_TEST_DATA = {
    "adapters": [
        {"search": "generic", "exp": "generic"},
        {"search": "active_directory_adapter", "exp": "active_directory"},
        {"search": "active_directory", "exp": "active_directory"},
    ],
    "single_field": {
        "search": "generic:username",
        "exp": "specific_data.data.username",
    },
    "fields": [
        {"search": "username", "exp": ["specific_data.data.username"]},
        {"search": "generic:username", "exp": ["specific_data.data.username"]},
        {"search": "mail", "exp": ["specific_data.data.mail"]},
        {"search": "generic:mail", "exp": ["specific_data.data.mail"]},
        {
            "search": "generic:mail,username",
            "exp": ["specific_data.data.mail", "specific_data.data.username"],
        },
        {
            "search": "active_directory:username",
            "exp": ["adapters_data.active_directory_adapter.username"],
        },
        {
            "search": "adapters_data.active_directory_adapter.username",
            "exp": ["adapters_data.active_directory_adapter.username"],
        },
        {
            "search": "*,*,username",
            "exp": ["specific_data", "specific_data.data.username"],
        },
    ],
    "val_fields": [
        {
            "search": ["active_directory:username", "generic:username", "mail"],
            "exp": [
                "adapters_data.active_directory_adapter.username",
                "specific_data.data.username",
                "specific_data.data.mail",
            ],
        }
    ],
}

DEVICES_TEST_DATA = {
    "adapters": [
        {"search": "generic", "exp": "generic"},
        {"search": "active_directory_adapter", "exp": "active_directory"},
        {"search": "active_directory", "exp": "active_directory"},
    ],
    "single_field": {
        "search": "generic:hostname",
        "exp": "specific_data.data.hostname",
    },
    "fields": [
        {
            "search": "network_interfaces.ips",
            "exp": ["specific_data.data.network_interfaces.ips"],
        },
        {
            "search": "generic:network_interfaces.ips",
            "exp": ["specific_data.data.network_interfaces.ips"],
        },
        {"search": "hostname", "exp": ["specific_data.data.hostname"]},
        {"search": "generic:hostname", "exp": ["specific_data.data.hostname"]},
        {
            "search": "generic:hostname,network_interfaces.ips",
            "exp": [
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
            ],
        },
        {
            "search": "active_directory:hostname",
            "exp": ["adapters_data.active_directory_adapter.hostname"],
        },
        {
            "search": "adapters_data.active_directory_adapter.hostname",
            "exp": ["adapters_data.active_directory_adapter.hostname"],
        },
        {
            "search": "*,*,hostname",
            "exp": ["specific_data", "specific_data.data.hostname"],
        },
    ],
    "val_fields": [
        {
            "search": [
                "active_directory:hostname",
                "generic:hostname",
                "network_interfaces.ips",
            ],
            "exp": [
                "adapters_data.active_directory_adapter.hostname",
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
            ],
        }
    ],
}


class TestBase(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, request, apicls):
        """Pass."""
        auth = utils.get_auth(request)

        api = apicls(auth=auth)

        assert isinstance(api._default_fields, tools.LIST)

        utils.check_apiobj(authobj=auth, apiobj=api)

        utils.check_apiobj_children(
            apiobj=api,
            labels=axonapi.api.users_devices.Labels,
            saved_query=axonapi.api.users_devices.SavedQuery,
            fields=axonapi.api.users_devices.Fields,
        )

        utils.check_apiobj_xref(apiobj=api, adapters=axonapi.api.adapters.Adapters)

        api_type = api._router._object_type

        if api_type == "users":
            api.TEST_DATA = USERS_TEST_DATA
        else:
            api.TEST_DATA = DEVICES_TEST_DATA

        api.ALL_FIELDS = api.fields.get()

        return api

    def get_single_asset(self, apiobj, fields=None, query=None, refetch=None):
        """Pass."""
        if refetch and not query:
            query = QUERY_ID(**refetch)

        data = apiobj._get(query=query, fields=fields, page_size=1)
        assert isinstance(data, dict)

        assets = data["assets"]
        assert len(assets) == 1

        assert isinstance(assets, tools.LIST)
        asset = assets[0]

        return asset

    def build_long_query(self, apiobj):
        """Pass."""
        single_field = apiobj.TEST_DATA["single_field"]["exp"]

        qtmpl = '({} == "{}")'.format
        vtmpl = "badwolf_{}".format

        long_query = [qtmpl(single_field, vtmpl(i)) for i in range(0, 1000)]

        return "not " + " or ".join(long_query)


@pytest.mark.parametrize("apicls", [axonapi.api.Users, axonapi.Devices], scope="class")
class TestBoth(TestBase):
    """Pass."""

    def test__count_post_false(self, apiobj):
        """Pass."""
        data = apiobj._count(use_post=False)
        assert isinstance(data, int)

    def test__count_query_len_forces_post(self, apiobj):
        """Pass."""
        long_query = self.build_long_query(apiobj)

        data = apiobj._count(query=long_query, use_post=False)
        assert isinstance(data, int)

        response = apiobj._auth._http._LAST_RESPONSE
        assert response.request.method == "POST"

    def test__get_post_false(self, apiobj):
        """Pass."""
        data = apiobj._get(page_size=1, use_post=False)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], tools.LIST)
        assert len(data["assets"]) == 1
        assert isinstance(data["assets"][0], dict)

    def test__get_query_len_forces_post(self, apiobj):
        """Pass."""
        long_query = self.build_long_query(apiobj)
        fields = [apiobj.TEST_DATA["single_field"]["exp"]]

        data = apiobj._get(query=long_query, fields=fields, page_size=1, use_post=False)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], tools.LIST)

        total = data["page"]["totalResources"]

        # FUTURE: overcome use_post ignoring limit
        if total < constants.MAX_PAGE_SIZE:
            assert len(data["assets"]) == total
        else:
            assert len(data["assets"]) == constants.MAX_PAGE_SIZE

        response = apiobj._auth._http._LAST_RESPONSE
        assert response.request.method == "POST"

    def test__get_by_id(self, apiobj):
        """Pass."""
        asset = self.get_single_asset(apiobj=apiobj)
        data = apiobj._get_by_id(id=asset["internal_axon_id"])
        assert isinstance(data, dict)

    def test_count(self, apiobj):
        """Pass."""
        data = apiobj.count()
        assert isinstance(data, int)

    def test_get(self, apiobj):
        """Pass."""
        data = apiobj.get(max_rows=1)
        assert isinstance(data, list)
        assert len(data) == 1


@pytest.mark.parametrize("apicls", [axonapi.api.Users, axonapi.Devices], scope="class")
class TestFields(TestBase):
    """Pass."""

    def test__get(self, apiobj):
        """Pass."""
        fields = apiobj.fields._get()
        assert isinstance(fields, dict)
        assert isinstance(fields["generic"], tools.LIST)
        assert isinstance(fields["specific"], dict)
        assert isinstance(fields["schema"], dict)

    def test_get(self, apiobj):
        """Pass."""
        fields = apiobj.fields.get()
        assert isinstance(fields, dict)
        assert isinstance(fields["generic"], dict)

    def test_find_adapter(self, apiobj):
        """Pass."""
        for info in apiobj.TEST_DATA["adapters"]:
            isearch = info["search"]
            iexp = info["exp"]
            searches = [
                isearch,
                isearch + ("_adapter" if not isearch.endswith("_adapter") else ""),
                isearch.upper(),
                isearch + "   ",
                "  " + isearch + "   ",
                iexp,
                iexp.upper(),
                iexp + "   ",
                "   " + iexp + "   ",
            ]
            for search in searches:
                name, obj_fields = apiobj.fields.find_adapter(
                    adapter=search, all_fields=apiobj.ALL_FIELDS
                )
                assert isinstance(name, tools.STR)
                assert isinstance(obj_fields, dict)
                assert name == info["exp"]

    def test_find_adapter_error_true(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.fields.find_adapter(
                adapter="badwolf", all_fields=apiobj.ALL_FIELDS, error=True
            )

    def test_find_adapter_error_false(self, apiobj):
        """Pass."""
        name, fields = apiobj.fields.find_adapter(
            adapter="badwolf", all_fields=apiobj.ALL_FIELDS, error=False
        )
        assert name is None
        assert fields == {}

    def test_find(self, apiobj):
        """Pass."""
        for info in apiobj.TEST_DATA["fields"]:
            isearch = info["search"]
            searches = [isearch, isearch.upper(), re.sub(":", " : ", isearch)]
            for search in searches:
                found = apiobj.fields.find(field=search, all_fields=apiobj.ALL_FIELDS)
                assert isinstance(found, tools.LIST)
                for x in found:
                    assert isinstance(x, tools.STR)
                assert found == info["exp"]

    def test_find_bad_adapter(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.fields.find(field="badwolf:badwolf", all_fields=apiobj.ALL_FIELDS)

    def test_find_bad_adapter_noerr(self, apiobj):
        """Pass."""
        found = apiobj.fields.find(
            field="badwolf:badwolf", all_fields=apiobj.ALL_FIELDS, error=False
        )
        assert isinstance(found, tools.LIST)
        assert not found

    def test_find_bad_field(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.fields.find("generic:badwolf", all_fields=apiobj.ALL_FIELDS)

    def test_find_bad_field_noerr(self, apiobj):
        """Pass."""
        found = apiobj.fields.find(
            field="generic:badwolf", all_fields=apiobj.ALL_FIELDS, error=False
        )
        assert isinstance(found, tools.LIST)
        assert not found

    def test_validatedefault_false(self, apiobj):
        """Pass."""
        for info in apiobj.TEST_DATA["val_fields"]:
            isearch = info["search"]
            iexp = info["exp"]
            found = apiobj.fields.validate(
                fields=isearch, all_fields=apiobj.ALL_FIELDS, default=False
            )
            assert isinstance(found, tools.LIST)
            assert found == iexp

    def test_validatedefault_true(self, apiobj):
        """Pass."""
        apifields = apiobj._default_fields

        for info in apiobj.TEST_DATA["val_fields"]:
            isearch = info["search"]
            iexp = list(info["exp"])
            found = apiobj.fields.validate(
                fields=isearch, all_fields=apiobj.ALL_FIELDS, default=True
            )
            assert isinstance(found, tools.LIST)

            for x in apifields:
                if x not in iexp:
                    iexp.append(x)

            assert sorted(found) == sorted(iexp)

    def test_validate_ignores(self, apiobj):
        """Pass."""
        found = apiobj.fields.validate(
            fields=[None, {}, [], ""], all_fields=apiobj.ALL_FIELDS, default=False
        )
        assert isinstance(found, tools.LIST)
        assert not found

    def test_validate_nofields_default_false(self, apiobj):
        """Pass."""
        found = apiobj.fields.validate(all_fields=apiobj.ALL_FIELDS, default=False)
        assert isinstance(found, tools.LIST)
        assert not found

    def test_validate_nofields_default_true(self, apiobj):
        """Pass."""
        found = apiobj.fields.validate(all_fields=apiobj.ALL_FIELDS, default=True)
        assert isinstance(found, tools.LIST)
        assert found == apiobj._default_fields


@pytest.mark.parametrize("apicls", [axonapi.api.Users, axonapi.Devices], scope="class")
class TestLabels(TestBase):
    """Pass."""

    def test__get(self, apiobj):
        """Pass."""
        fields = apiobj.labels._get()
        assert isinstance(fields, list)
        for x in fields:
            assert isinstance(x, tools.STR)

    def test_get(self, apiobj):
        """Pass."""
        fields = apiobj.labels._get()
        assert isinstance(fields, list)
        for x in fields:
            assert isinstance(x, tools.STR)

    def test__add_get_remove(self, apiobj):
        """Pass."""
        fields = ["labels"]
        labels = ["badwolf"]

        # get a single asset to add a label to
        asset_tolabel = self.get_single_asset(
            apiobj=apiobj, fields=fields, query=None, refetch=None
        )

        id_tolabel = asset_tolabel["internal_axon_id"]
        assert isinstance(id_tolabel, tools.STR)

        # add the label to the asset
        result_tolabel = apiobj.labels._add(labels=labels, ids=[id_tolabel])
        assert result_tolabel == 1

        # re-get the asset and check that it has the label
        asset_haslabel = self.get_single_asset(
            apiobj=apiobj, fields=fields, query=None, refetch=asset_tolabel
        )

        id_haslabel = asset_haslabel["internal_axon_id"]
        assert isinstance(id_haslabel, tools.STR)

        for label in labels:
            assert label in asset_haslabel["labels"]

        # check that the label is in all the labels on the system
        alllabels = apiobj.labels._get()
        assert isinstance(alllabels, tools.LIST)

        for label in alllabels:
            assert isinstance(label, tools.STR)

        for label in labels:
            assert label in alllabels

        # remove the label from an asset
        result_nolabel = apiobj.labels._remove(labels=labels, ids=[id_haslabel])
        assert result_nolabel == 1

        # re-get the asset and check that it has the label
        asset_nolabel = self.get_single_asset(
            apiobj=apiobj, fields=fields, query=None, refetch=asset_haslabel
        )
        id_nolabel = asset_nolabel["internal_axon_id"]
        assert isinstance(id_nolabel, tools.STR)

        assert id_tolabel == id_nolabel == id_haslabel

        for label in labels:
            assert label not in asset_nolabel.get("labels", []), asset_nolabel

    def test_add_get_remove(self, apiobj):
        """Pass."""
        fields = ["labels"]
        labels = ["badwolf"]

        # get a single asset to add a label to
        asset_tolabel = self.get_single_asset(
            apiobj=apiobj, fields=fields, query=None, refetch=None
        )

        id_tolabel = asset_tolabel["internal_axon_id"]
        assert isinstance(id_tolabel, tools.STR)

        # add the label to the asset
        result_tolabel = apiobj.labels.add(labels=labels, rows=[asset_tolabel])
        assert result_tolabel == 1

        # re-get the asset and check that it has the label
        asset_haslabel = self.get_single_asset(
            apiobj=apiobj, fields=fields, query=None, refetch=asset_tolabel
        )

        id_haslabel = asset_haslabel["internal_axon_id"]
        assert isinstance(id_haslabel, tools.STR)

        for label in labels:
            assert label in asset_haslabel["labels"]

        # check that the label is in all the labels on the system
        alllabels = apiobj.labels.get()
        assert isinstance(alllabels, tools.LIST)

        for label in alllabels:
            assert isinstance(label, tools.STR)

        for label in labels:
            assert label in alllabels

        # remove the label from the asset
        nolabel_result = apiobj.labels.remove(labels=labels, rows=[asset_haslabel])
        assert nolabel_result == 1

        # re-get the asset and check that it has the label
        asset_nolabel = self.get_single_asset(
            apiobj=apiobj, fields=fields, query=None, refetch=asset_haslabel
        )
        id_nolabel = asset_nolabel["internal_axon_id"]
        assert isinstance(id_nolabel, tools.STR)

        assert id_tolabel == id_nolabel == id_haslabel

        for label in labels:
            assert label not in asset_nolabel.get("labels", []), asset_nolabel


@pytest.mark.parametrize("apicls", [axonapi.api.Users, axonapi.Devices], scope="class")
class TestSavedQuery(TestBase):
    """Pass."""

    def test__get(self, apiobj):
        """Pass."""
        data = apiobj.saved_query._get()
        assert isinstance(data, dict)

        assets = data["assets"]
        assert isinstance(assets, tools.LIST)

        for asset in assets:
            assert isinstance(asset, dict)

            assert asset["query_type"] in ["saved"]

            str_keys = [
                "associated_user_name",
                "date_fetched",
                "name",
                "query_type",
                "timestamp",
                "user_id",
                "uuid",
            ]

            for str_key in str_keys:
                val = asset.pop(str_key)
                assert isinstance(val, tools.STR)

            predefined = asset.pop("predefined", False)
            assert isinstance(predefined, bool)

            view = asset.pop("view")
            assert isinstance(view, dict)

            colsizes = view.pop("coloumnSizes", [])
            assert isinstance(colsizes, tools.LIST)

            colfilters = view.pop("colFilters", {})
            assert isinstance(colfilters, dict)
            for k, v in colfilters.items():
                assert isinstance(k, tools.STR)
                assert isinstance(v, tools.STR)

            for x in colsizes:
                assert isinstance(x, tools.INT)

            fields = view.pop("fields")
            assert isinstance(fields, tools.LIST)

            for x in fields:
                assert isinstance(x, tools.STR)

            page = view.pop("page", 0)
            assert isinstance(page, tools.INT)

            pagesize = view.pop("pageSize", 0)
            assert isinstance(pagesize, tools.INT)

            sort = view.pop("sort")
            assert isinstance(sort, dict)

            sort_desc = sort.pop("desc")
            assert isinstance(sort_desc, bool)

            sort_field = sort.pop("field")
            assert isinstance(sort_field, tools.STR)

            query = view.pop("query")
            assert isinstance(query, dict)

            qfilter = query.pop("filter")
            assert isinstance(qfilter, tools.STR)

            qexprs = query.pop("expressions", [])
            assert isinstance(qexprs, tools.LIST)

            historical = view.pop("historical", None)
            assert historical is None or isinstance(historical, tools.SIMPLE)
            # FUTURE: what else besides None?? bool?

            for qexpr in qexprs:
                assert isinstance(qexpr, dict)

                compop = qexpr.pop("compOp")
                field = qexpr.pop("field")
                idx = qexpr.pop("i", 0)
                leftbracket = qexpr.pop("leftBracket")
                rightbracket = qexpr.pop("rightBracket")
                logicop = qexpr.pop("logicOp")
                notflag = qexpr.pop("not")
                value = qexpr.pop("value")
                obj = qexpr.pop("obj", False)
                nesteds = qexpr.pop("nested", [])
                fieldtype = qexpr.pop("fieldType", "")

                assert isinstance(compop, tools.STR)
                assert isinstance(field, tools.STR)
                assert isinstance(idx, tools.INT)
                assert isinstance(leftbracket, bool)
                assert isinstance(rightbracket, bool)
                assert isinstance(logicop, tools.STR)
                assert isinstance(notflag, bool)
                assert isinstance(value, tools.SIMPLE) or value is None
                assert isinstance(obj, bool)
                assert isinstance(nesteds, tools.LIST)
                assert isinstance(fieldtype, tools.STR)

                for nested in nesteds:
                    assert isinstance(nested, dict)

                    ncondition = nested.pop("condition")
                    assert isinstance(ncondition, tools.STR)

                    nexpr = nested.pop("expression")
                    assert isinstance(nexpr, dict)

                    nidx = nested.pop("i")
                    assert isinstance(nidx, tools.INT)

                    assert not nested, list(nested)

                assert not qexpr, list(qexpr)

            assert not query, list(query)
            assert not sort, list(sort)
            assert not view, list(view)
            assert not asset, list(asset)

    def test__get_query(self, apiobj):
        """Pass."""
        query = 'name == regex(".*", "i")'
        data = apiobj.saved_query._get(query=query)
        assert isinstance(data, dict)

        assets = data["assets"]
        assert isinstance(assets, tools.LIST)
        assert len(data["assets"]) == data["page"]["totalResources"]

    def test_get(self, apiobj):
        """Pass."""
        rows = apiobj.saved_query.get()
        assert isinstance(rows, tools.LIST)
        for row in rows:
            assert isinstance(row, dict)

    def test_get_notfound_noerror(self, apiobj):
        """Pass."""
        query = 'name == "badwolf_notfound"'
        data = apiobj.saved_query.get(query=query)
        assert isinstance(data, tools.LIST)
        assert not data

    def test_find_by_id(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get()
        found = apiobj.saved_query.find_by_id(value=data[0]["uuid"])
        assert isinstance(found, dict)

    def test_find_by_id_notfound(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.saved_query.find_by_id(value="badwolf")

    def test_find_by_name(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get()
        found = apiobj.saved_query.find_by_name(value=data[0]["name"])
        assert isinstance(found, dict)

    def test_find_by_name_regex(self, apiobj):
        """Pass."""
        found = apiobj.saved_query.find_by_name(value=".*", use_regex=True)
        assert isinstance(found, list)
        assert len(found) >= 1

    def test_find_by_name_notflag(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get()
        found = apiobj.saved_query.find_by_name(value=data[0]["name"], not_flag=True)
        assert isinstance(found, list)
        assert len(found) == len(data) - 1

    def test__add_get_delete(self, apiobj):
        """Pass."""
        name = "badwolf_test__add_get_delete"

        asset = self.get_single_asset(apiobj=apiobj, query=None, refetch=None)

        query = QUERY_ID(**asset)

        fields = [apiobj.TEST_DATA["single_field"]["exp"]]

        added = apiobj.saved_query._add(name=name, query=query, fields=fields)
        assert isinstance(added, tools.STR)

        got = apiobj.saved_query._get(query='name == "{}"'.format(name))
        assert isinstance(got, dict)
        assert isinstance(got["assets"], list)
        assert len(got["assets"]) == 1
        assert isinstance(got["assets"][0], dict)

        deleted = apiobj.saved_query._delete(ids=[added])
        assert not deleted

        re_got = apiobj.saved_query._get(query='name == "{}"'.format(name))
        assert isinstance(re_got, dict)
        assert isinstance(re_got["assets"], list)
        assert len(re_got["assets"]) == 0

    def test_add_delete(self, apiobj):
        """Pass."""
        name = "badwolf_test_add_delete"

        asset = self.get_single_asset(apiobj=apiobj, query=None, refetch=None)

        query = QUERY_ID(**asset)

        added = apiobj.saved_query.add(name=name, query=query)
        assert isinstance(added, dict)
        assert added["name"] == name
        assert added["view"]["query"]["filter"] == query

        deleted = apiobj.saved_query.delete(rows=added)
        assert not deleted

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.saved_query.find_by_name(name)

    def test_add_delete_sort(self, apiobj):
        """Pass."""
        name = "badwolf_test_add_delete_sort"
        single_field = apiobj.TEST_DATA["single_field"]
        asset = self.get_single_asset(apiobj=apiobj, query=None, refetch=None)

        query = QUERY_ID(**asset)

        added = apiobj.saved_query.add(
            name=name, query=query, sort=single_field["search"]
        )
        assert isinstance(added, dict)
        assert added["name"] == name
        assert added["view"]["query"]["filter"] == query
        assert added["view"]["sort"]["field"] == single_field["exp"]

        deleted = apiobj.saved_query.delete(rows=added)
        assert not deleted

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.saved_query.find_by_name(name)

    def test_add_delete_colfilter(self, apiobj):
        """Pass."""
        name = "badwolf_test_add_delete_colfilter"
        single_field = apiobj.TEST_DATA["single_field"]
        asset = self.get_single_asset(apiobj=apiobj, query=None, refetch=None)

        column_filters = {single_field["search"]: "a"}
        exp_column_filters = {single_field["exp"]: "a"}

        query = QUERY_ID(**asset)

        added = apiobj.saved_query.add(
            name=name, query=query, column_filters=column_filters
        )
        assert isinstance(added, dict)
        assert added["name"] == name
        assert added["view"]["query"]["filter"] == query
        assert added["view"]["colFilters"] == exp_column_filters

        deleted = apiobj.saved_query.delete(rows=added)
        assert not deleted

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.saved_query.find_by_name(name)


'''

@pytest.mark.parametrize("apicls", [axonapi.api.Users, axonapi.Devices], scope="class")
class TestUsersDevices(TestBase):
    """Pass."""

    def test__get_query_fields_none(self, apiobj):
        """Test private get."""
        api_type = apiobj._router._object_type

        gargs = dict(fields=None, row_start=0, page_size=1, query=None, use_post=False)

        data = apiobj._get(**gargs)

        assert is_type.dict(data)
        assert "assets" in data
        assert is_type.list(data["assets"])

        if not data["assets"]:
            msg = "No {t} on system, unable to test _get"
            msg = msg.format(t=api_type)
            pytest.skip(msg)

        assert len(data["assets"]) == 1

    def test__get_post_false(
        self, apiobj, fields_list_manual_query, fields_list_manual
    ):
        """Test private get."""
        api_type = apiobj._router._object_type

        gargs = dict(
            fields=fields_list_manual,
            row_start=0,
            page_size=1,
            query=fields_list_manual_query,
            use_post=False,
        )

        data = apiobj._get(**gargs)

        assert is_type.dict(data)
        assert "assets" in data
        assert is_type.list(data["assets"])

        if not data["assets"]:
            msg = "No {t} on system, unable to test _get"
            msg = msg.format(t=api_type)
            pytest.skip(msg)

        assert len(data["assets"]) == 1

        for entry in data["assets"]:
            assert is_type.dict(entry)
            assert "adapters" in entry
            for field in fields_list_manual:
                assert field in entry

    # FUTURE: use_post = True ignores page_size (limit) and just returns 2000 items
    def test__get_post_true(self, apiobj, fields_list_manual_query, fields_list_manual):
        """Test private get."""
        api_type = apiobj._router._object_type

        gargs = dict(
            fields=fields_list_manual,
            row_start=0,
            page_size=1,
            query=fields_list_manual_query,
            use_post=True,
        )

        data = apiobj._get(**gargs)

        assert is_type.dict(data)
        assert "assets" in data
        assert is_type.list(data["assets"])

        if not data["assets"]:
            msg = "No {t} on system, unable to test _get"
            msg = msg.format(t=api_type)
            pytest.skip(msg)

        if data["page"]["totalResources"] < 2000:
            assert len(data["assets"]) == data["page"]["totalResources"]
        else:
            assert len(data["assets"]) == 2000

        for entry in data["assets"]:
            assert is_type.dict(entry)
            assert "adapters" in entry
            for field in fields_list_manual:
                assert field in entry

    def test__get_long_query_uses_post(self, apiobj):
        """Pass."""
        api_type = apiobj._router._object_type

        data = apiobj._get(query=LONG_QUERY, page_size=1)

        assert is_type.dict(data)
        assert "assets" in data
        assert is_type.list(data["assets"])

        if not data["assets"]:
            msg = "No {t} on system, unable to test _get"
            msg = msg.format(t=api_type)
            pytest.skip(msg)

        assert apiobj._auth.http._LAST_RESPONSE.request.method == "POST"

        if data["page"]["totalResources"] < 2000:
            assert len(data["assets"]) == data["page"]["totalResources"]
        else:
            assert len(data["assets"]) == 2000

    def test_count_long_query_uses_post(self, apiobj):
        """Pass."""
        data = apiobj.count(query=LONG_QUERY)
        assert is_type.int(data)
        assert apiobj._auth.http._LAST_RESPONSE.request.method == "POST"

    @pytest.mark.parametrize("query", [None, QUERY_ID_EXISTS])
    @pytest.mark.parametrize("use_post", [True, False])
    def test_count(self, apiobj, query, use_post):
        """Test count."""
        data = apiobj.count(query=query, use_post=use_post)
        assert is_type.int(data)

    def test_get_manual(self, apiobj, fields_list_manual, single_asset_query):
        """Pass."""
        data = apiobj.get(
            query=single_asset_query,
            manual_fields=fields_list_manual,
            count_max=1,
            count_error=False,
        )
        assert is_type.dict(data)

    def test_get_validate(self, apiobj, fields_dict_mix, single_asset_query):
        """Pass."""
        data = apiobj.get(
            query=single_asset_query, count_max=1, count_error=False, **fields_dict_mix
        )
        assert is_type.dict(data)

    def test_get_cntmax_error(self, apiobj, fields_dict_mix):
        """Pass."""
        with pytest.raises(exceptions.TooManyObjectsFound):
            apiobj.get(count_max=1, **fields_dict_mix)

    def test_get_cntmax_noerror1(self, apiobj, fields_dict_mix):
        """Pass."""
        data = apiobj.get(count_max=1, count_error=False, **fields_dict_mix)
        assert is_type.dict(data)

    def test_get_cntmax_noerror2(self, apiobj, fields_dict_mix):
        """Pass."""
        data = apiobj.get(count_max=2, count_error=False, **fields_dict_mix)
        assert is_type.list(data)
        assert len(data) == 2

    def test_get_cntmin_error(self, apiobj, fields_dict_mix):
        """Pass."""
        with pytest.raises(exceptions.TooFewObjectsFound):
            apiobj.get(
                query='not (specific_data.data.id == ({"$exists":true,"$ne": ""}))',
                count_min=1,
                **fields_dict_mix
            )

    def test_get_cntmin_noerror(self, apiobj, fields_dict_mix):
        """Pass."""
        data = apiobj.get(
            query='not (specific_data.data.id == ({"$exists":true,"$ne": ""}))',
            count_min=1,
            count_error=False,
            **fields_dict_mix
        )
        assert len(data) == 0

    def test_get_cntmaxmin_noerror(self, apiobj, fields_dict_mix):
        """Pass."""
        data = apiobj.get(
            query='not (specific_data.data.id == ({"$exists":true,"$ne": ""}))',
            count_min=1,
            count_max=1,
            count_error=False,
            **fields_dict_mix
        )
        assert not data

    def test_get_cntmaxmin_error(self, apiobj, fields_dict_mix):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get(
                query='not (specific_data.data.id == ({"$exists":true,"$ne": ""}))',
                count_min=1,
                count_max=1,
                **fields_dict_mix
            )

    def test_sq_get_name(self, apiobj, test_sq_get):
        """Pass."""
        name = test_sq_get[0]["name"]
        data = apiobj.saved_query.find_by_name(value=name)
        assert is_type.dict(data)
        assert "name" in data
        assert is_type.str(data["name"])

    def test_sq_get_name_re(self, apiobj, test_sq_get):
        """Pass."""
        name = test_sq_get[0]["name"][0]
        data = apiobj.saved_query.find_by_name(value=name, use_regex=True)
        assert is_type.lod(data)
        assert len(data) >= 1

    def test_get_by_id(self, apiobj, single_asset):
        """Pass."""
        data = apiobj.get_by_id(single_asset["internal_axon_id"])
        assert is_type.dict(data)
        assert data
        keys = ["generic", "internal_axon_id", "specific", "accurate_for_datetime"]
        for key in keys:
            assert key in data

    def test_get_by_id_fail(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get_by_id("BADWOLF")

    def test_get_by_sq(self, apiobj, test_sq_get):
        """Pass."""
        name = test_sq_get[0]["name"]
        data = apiobj.get_by_saved_query(name=name)
        assert is_type.list(data)
        keys = ["adapter_list_length", "adapters", "internal_axon_id"]
        for entry in data:
            for key in keys:
                assert key in entry

    def test_get_by_fv_re(self, apiobj, fields_dict_manual):
        """Pass."""
        for k, v in fields_dict_manual.items():
            adapter_name = k
            field_name = v[0]
            break

        data = apiobj.get_by_field_value(
            value="a",
            name=field_name,
            adapter_name=adapter_name,
            use_regex=True,
            **fields_dict_manual
        )
        assert is_type.list(data)
        assert data
        keys = ["adapter_list_length", "adapters", "internal_axon_id", field_name]
        for entry in data:
            for key in keys:
                assert key in entry

    def test_get_by_fv(self, apiobj, single_asset, fields_dict_manual):
        """Pass."""
        for k, v in fields_dict_manual.items():
            adapter_name = k
            field_name = v[0]
            break

        field_value = single_asset[field_name]
        if is_type.list(field_value):
            field_value = field_value[0]

        data = apiobj.get_by_field_value(
            value=field_value,
            name=field_name,
            adapter_name=adapter_name,
            **fields_dict_manual
        )

        assert is_type.dict(data)
        keys = ["adapter_list_length", "adapters", "internal_axon_id", field_name]
        for key in keys:
            assert key in data

    def test_get_by_fv_err(self, apiobj, fields_dict_manual):
        """Pass."""
        for k, v in fields_dict_manual.items():
            adapter_name = k
            field_name = v[0]
            break

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get_by_field_value(
                value="askdjfsdfsadgasg",
                name=field_name,
                adapter_name=adapter_name,
                **fields_dict_manual
            )

    def test_fields_parser_dupe(self, apiobj):
        """Pass."""
        raw_fields = apiobj.fields._get()
        raw_fields["generic"].append(raw_fields["generic"][0])
        parser = axonapi.api.users_devices.ParserFields(parent=apiobj, raw=raw_fields)
        with pytest.raises(exceptions.ApiError):
            parser.parse()

    # TODO: RE-DO!
    def test_reports_adapter(self, apiobj, all_assets, all_fields):
        """Pass."""
        report = apiobj.report_adapters(rows=all_assets, all_fields=all_fields)
        assert is_type.list(report)
        assert tools.nest_depth(report) >= 3

    def test_reports_adapter_serial(self, apiobj, all_assets, all_fields):
        """Pass."""
        report = apiobj.report_adapters(
            rows=all_assets, all_fields=all_fields, serial=True
        )
        assert is_type.list(report)
        assert tools.nest_depth(report) == 2


@pytest.mark.needs_url
@pytest.mark.needs_key_creds
@pytest.mark.parametrize("creds", ["creds_key"], indirect=True, scope="class")
class TestUsers(object):
    """Pass."""

    FIELDS = ["specific_data.data.username", "specific_data.data.mail"]

    QUERY = " and ".join([QUERY_TMPL(f) for f in FIELDS])

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds):
        """Pass."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        api = axonapi.api.Users(auth=auth)
        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)
        assert is_type.dict(api._default_fields)
        assert isinstance(api._router, axonapi.api.routers.Router)
        assert isinstance(api.labels, axonapi.api.mixins.Child)
        assert isinstance(api.labels, axonapi.api.users_devices.Labels)
        assert isinstance(api.saved_query, axonapi.api.mixins.Child)
        assert isinstance(api.saved_query, axonapi.api.users_devices.SavedQuery)
        assert isinstance(api.fields, axonapi.api.mixins.Child)
        assert isinstance(api.fields, axonapi.api.users_devices.Fields)
        assert isinstance(api.adapters, axonapi.api.adapters.Adapters)
        return api

    @pytest.fixture(scope="class")
    def all_assets(self, apiobj):
        """Pass."""
        data = apiobj.get(
            query=self.QUERY, manual_fields=self.FIELDS, count_max=10, count_error=False
        )
        assert is_type.list(data)

        if not data:
            reason = "No users returned with fields: {}"
            reason = reason.format(self.FIELDS)
            pytest.skip(reason=reason)

        for asset in data:
            assert is_type.dict(asset)
            for x in self.FIELDS:
                assert x in asset
                assert asset[x]

        return data

    @pytest.fixture(scope="class")
    def single_asset(self, apiobj):
        """Pass."""
        data = apiobj._get(query=self.QUERY, page_size=1, fields=self.FIELDS)
        assert is_type.dict(data)

        assets = data["assets"]
        assert is_type.list(assets)

        if not assets:
            reason = "No users returned with fields: {}"
            reason = reason.format(self.FIELDS)
            pytest.skip(reason=reason)

        assert len(assets) == 1

        asset = assets[0]
        assert is_type.dict(asset)

        for x in self.FIELDS:
            assert x in asset
            assert asset[x]

        return asset

    def test_get_by_username(self, apiobj, single_asset):
        """Pass."""
        value = single_asset["specific_data.data.username"]
        value = value[0] if is_type.list(value) else value

        data = apiobj.get_by_username(value=value, **{"generic": self.FIELDS})

        assert is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]

    def test_get_by_mail(self, apiobj, single_asset):
        """Pass."""
        value = single_asset["specific_data.data.mail"]
        value = value[0] if is_type.list(value) else value

        data = apiobj.get_by_mail(value=value, **{"generic": self.FIELDS})

        assert is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]


@pytest.mark.needs_url
@pytest.mark.needs_key_creds
@pytest.mark.parametrize("creds", ["creds_key"], indirect=True, scope="class")
class TestDevices(object):
    """Pass."""

    FIELDS = [
        "specific_data.data.network_interfaces.ips",
        "specific_data.data.network_interfaces.mac",
        "specific_data.data.hostname",
    ]

    QUERY = " and ".join([QUERY_TMPL(f) for f in FIELDS])

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds):
        """Pass."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        api = axonapi.api.Devices(auth=auth)
        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)
        assert is_type.dict(api._default_fields)
        assert isinstance(api._router, axonapi.api.routers.Router)
        assert isinstance(api.labels, axonapi.api.mixins.Child)
        assert isinstance(api.labels, axonapi.api.users_devices.Labels)
        assert isinstance(api.saved_query, axonapi.api.mixins.Child)
        assert isinstance(api.saved_query, axonapi.api.users_devices.SavedQuery)
        assert isinstance(api.fields, axonapi.api.mixins.Child)
        assert isinstance(api.fields, axonapi.api.users_devices.Fields)
        assert isinstance(api.adapters, axonapi.api.adapters.Adapters)
        return api

    @pytest.fixture(scope="class")
    def all_assets(self, apiobj):
        """Pass."""
        data = apiobj.get(
            query=self.QUERY, manual_fields=self.FIELDS, count_max=10, count_error=False
        )
        assert is_type.list(data)

        if not data:
            reason = "No devices returned with fields: {}"
            reason = reason.format(self.FIELDS)
            pytest.skip(reason=reason)

        for asset in data:
            assert is_type.dict(asset)
            for x in self.FIELDS:
                assert x in asset
                assert asset[x]

        return data

    def test_get_by_hostname(self, apiobj, all_assets):
        """Pass."""
        value = all_assets[0]["specific_data.data.hostname"]
        value = value[0] if is_type.list(value) else value

        data = apiobj.get_by_hostname(value=value, **{"generic": self.FIELDS})

        assert is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]

    def test_get_by_mac(self, apiobj, all_assets):
        """Pass."""
        value = all_assets[0]["specific_data.data.network_interfaces.mac"]
        value = value[0] if is_type.list(value) else value

        data = apiobj.get_by_mac(value=value, **{"generic": self.FIELDS})

        assert is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]

    def test_get_by_ip(self, apiobj, all_assets):
        """Pass."""
        value = all_assets[0]["specific_data.data.network_interfaces.ips"]
        value = value[0] if is_type.list(value) else value

        data = apiobj.get_by_ip(value=value, **{"generic": self.FIELDS})

        assert is_type.dict(data)

        for x in self.FIELDS:
            assert x in data
            assert data[x]

    def test_get_by_in_subnet(self, apiobj, all_assets):
        """Pass."""
        value = all_assets[0]["specific_data.data.network_interfaces.ips"]
        value = value[0] if is_type.list(value) else value

        search = "{}/32".format(value)
        data = apiobj.get_by_in_subnet(value=search, **{"generic": self.FIELDS})

        assert is_type.list(data)
        assert len(data) == 1

        for asset in data:
            assert is_type.dict(asset)
            for x in self.FIELDS:
                assert x in asset
                assert asset[x]

    def test_get_by_not_in_subnet(self, apiobj, all_assets):
        """Pass."""
        value = all_assets[0]["specific_data.data.network_interfaces.ips"]
        value = value[0] if is_type.list(value) else value
        regex = re.compile(value)

        search = "{}/32".format(value)
        data = apiobj.get_by_not_in_subnet(value=search, **{"generic": self.FIELDS})

        assert is_type.list(data)

        for asset in data:
            assert is_type.dict(asset)
            ips = asset.get("specific_data.data.network_interfaces.ips", [])
            ips = axonapi.tools.listify(ips)
            for ip in ips:
                match = regex.match(ip)
                assert not match
'''


@pytest.mark.parametrize(
    "apicls", [(axonapi.api.Users), (axonapi.Devices)], scope="class"
)
class TestParsedFields(TestBase):
    """Pass."""

    def test_fields(self, apiobj):
        """Pass."""
        raw = apiobj.fields._get()
        parser = axonapi.api.users_devices.ParserFields(raw=raw, parent=apiobj)
        fields = parser.parse()

        with pytest.raises(exceptions.ApiError):
            parser._exists("generic", fields, "dumb test")

        assert isinstance(fields, dict)

        for aname, afields in fields.items():
            assert not aname.endswith("_adapter")
            assert isinstance(afields, dict)

            if aname == "generic":
                gall_data = afields.pop("all_data")
                assert isinstance(gall_data, dict)

                gall_data_name = gall_data.pop("name")
                gall_data_type = gall_data.pop("type")
                gall_data_prefix = gall_data.pop("adapter_prefix")
                gall_data_title = gall_data.pop("title")

                assert not gall_data, list(gall_data)
                assert gall_data_name == "specific_data.data"
                assert gall_data_type == "array"
                assert gall_data_prefix == "specific_data"
                assert gall_data_title == "All data subsets for generic adapter"

                gall = afields.pop("all")
                assert isinstance(gall, dict)

                gall_name = gall.pop("name")
                gall_type = gall.pop("type")
                gall_prefix = gall.pop("adapter_prefix")
                gall_title = gall.pop("title")

                assert not gall, list(gall)
                assert gall_name == "specific_data"
                assert gall_type == "array"
                assert gall_prefix == "specific_data"
                assert gall_title == "All data for generic adapter"

            else:
                graw = afields.pop("raw")
                assert isinstance(graw, dict)
                assert graw["name"].endswith(".raw")

                gall = afields.pop("all")
                assert isinstance(gall, dict)
                assert gall["name"] == "adapters_data.{}_adapter".format(aname)

            for fname, finfo in afields.items():
                self.val_field(fname, finfo, aname)

    def val_field(self, fname, finfo, aname):
        """Pass."""
        assert isinstance(finfo, dict)

        # common
        name = finfo.pop("name")
        type = finfo.pop("type")
        prefix = finfo.pop("adapter_prefix")
        title = finfo.pop("title")

        assert isinstance(name, tools.STR) and name
        assert isinstance(title, tools.STR) and title
        assert isinstance(prefix, tools.STR) and prefix
        assert isinstance(type, tools.STR) and type

        # uncommon
        items = finfo.pop("items", {})
        sort = finfo.pop("sort", False)
        unique = finfo.pop("unique", False)
        branched = finfo.pop("branched", False)
        enums = finfo.pop("enum", [])
        description = finfo.pop("description", "")
        dynamic = finfo.pop("dynamic", False)
        format = finfo.pop("format", "")

        assert isinstance(items, dict)
        assert isinstance(sort, bool)
        assert isinstance(unique, bool)
        assert isinstance(branched, bool)
        assert isinstance(enums, tools.LIST)
        assert isinstance(description, tools.STR)
        assert isinstance(dynamic, bool)
        assert isinstance(format, tools.STR)

        assert not finfo, list(finfo)

        assert type in FIELD_TYPES, type

        if name not in ["labels", "adapters", "internal_axon_id"]:
            if aname == "generic":
                assert name.startswith("specific_data")
            else:
                assert name.startswith(prefix)

        for enum in enums:
            assert isinstance(enum, tools.STR) or tools.is_int(enum)

        if format:
            assert format in FIELD_FORMATS, format

        val_items(aname=aname, items=items)


@pytest.mark.parametrize(
    "apicls", [(axonapi.api.Users), (axonapi.Devices)], scope="class"
)
class TestRawFields(TestBase):
    """Pass."""

    def test_fields(self, apiobj):
        """Pass."""
        raw = apiobj.fields._get()
        assert isinstance(raw, dict)

        schema = raw.pop("schema")
        generic = raw.pop("generic")
        specific = raw.pop("specific")

        assert not raw, list(raw)
        assert isinstance(schema, dict)
        assert isinstance(generic, list)
        assert isinstance(specific, dict)

        generic_schema = schema.pop("generic")
        specific_schema = schema.pop("specific")

        assert isinstance(generic_schema, dict)
        assert isinstance(specific_schema, dict)
        assert not schema, list(schema)

        self.val_schema(aname="generic", schema=generic_schema)

        self.val_fields(aname="generic", afields=generic)

        for aname, afields in specific.items():
            self.val_fields(aname=aname, afields=afields)

            aschema = specific_schema.pop(aname)

            assert isinstance(aschema, dict)

            self.val_schema(aname=aname, schema=aschema)

        assert not specific_schema, list(specific_schema)

    def val_schema(self, aname, schema):
        """Pass."""
        assert isinstance(schema, dict)

        items = schema.pop("items")
        required = schema.pop("required")
        type = schema.pop("type")

        assert not schema, list(schema)

        assert isinstance(items, tools.LIST)
        assert isinstance(required, tools.LIST)
        assert type == "array"

        for req in required:
            assert isinstance(req, tools.STR)

        for item in items:
            assert item
            val_items(aname=aname, items=item)

    def val_fields(self, aname, afields):
        """Pass."""
        assert isinstance(afields, tools.LIST)

        for field in afields:
            # common
            name = field.pop("name")
            title = field.pop("title")
            type = field.pop("type")

            assert isinstance(name, tools.STR) and name
            assert isinstance(title, tools.STR) and title
            assert isinstance(type, tools.STR) and type

            assert type in ["array", "string", "integer", "number", "bool"]

            # uncommon
            branched = field.pop("branched", False)
            description = field.pop("description", "")
            enums = field.pop("enum", [])
            format = field.pop("format", "")
            items = field.pop("items", {})
            sort = field.pop("sort", False)
            unique = field.pop("unique", False)
            dynamic = field.pop("dynamic", False)

            assert isinstance(branched, bool)
            assert isinstance(description, tools.STR)
            assert isinstance(enums, tools.LIST)
            assert isinstance(format, tools.STR)
            assert isinstance(items, dict)
            assert isinstance(sort, bool)
            assert isinstance(unique, bool)
            assert isinstance(dynamic, bool)

            assert not field, list(field)

            for enum in enums:
                assert isinstance(enum, tools.STR) or tools.is_int(enum)

            val_items(aname=aname, items=items)


def val_items(aname, items):
    """Pass."""
    assert isinstance(items, dict)

    if items:
        # common
        type = items.pop("type")

        assert isinstance(type, tools.STR) and type
        assert type in FIELD_TYPES, type

        # uncommon
        enums = items.pop("enum", [])
        format = items.pop("format", "")
        iitems = items.pop("items", [])
        name = items.pop("name", "")
        title = items.pop("title", "")
        description = items.pop("description", "")
        branched = items.pop("branched", False)
        dynamic = items.pop("dynamic", False)

        if format:
            assert format in SCHEMA_FIELD_FORMATS, format

        assert isinstance(enums, tools.LIST)
        assert isinstance(iitems, tools.LIST) or isinstance(iitems, dict)
        assert isinstance(format, tools.STR)
        assert isinstance(name, tools.STR)
        assert isinstance(title, tools.STR)
        assert isinstance(description, tools.STR)
        assert isinstance(branched, bool)
        assert isinstance(dynamic, bool)

        assert not items, list(items)

        for enum in enums:
            assert isinstance(enum, tools.STR) or tools.is_int(enum)

        if isinstance(iitems, dict):
            val_items(aname=aname, items=iitems)
        else:
            for iitem in iitems:
                val_items(aname=aname, items=iitem)
