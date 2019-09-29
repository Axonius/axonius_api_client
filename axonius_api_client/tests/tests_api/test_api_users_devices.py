# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re

import pytest

import axonius_api_client as axonapi
from axonius_api_client import exceptions, tools

from .. import utils

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

QUERY_ID = '((internal_axon_id == "{internal_axon_id}"))'.format
QUERY_EQ = '(({f} == "{v}"))'.format
QUERY_FIELD_EXISTS = '(({field} == ({{"$exists":true,"$ne": ""}})))'.format
"""
# multi
((internal_axon_id == ({"$exists":true,"$ne":""})))
    and
((specific_data.data.username == ({"$exists":true,"$ne":""})))
    and
((specific_data.data.mail == ({"$exists":true,"$ne":""})))

# single
((internal_axon_id == ({"$exists":true,"$ne":""})))

"""

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


class Base(object):
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
            reports=axonapi.api.users_devices.Reports,
        )

        utils.check_apiobj_xref(apiobj=api, adapters=axonapi.api.adapters.Adapters)

        api_type = api._router._object_type

        if api_type == "users":
            api.TEST_DATA = USERS_TEST_DATA
        else:
            api.TEST_DATA = DEVICES_TEST_DATA

        api.ALL_FIELDS = api.fields.get()

        return api

    def get_single_asset(
        self, apiobj, with_fields=None, fields=None, query=None, refetch=None
    ):
        """Pass."""
        if not query and refetch:
            query = QUERY_ID(**refetch)

        if not query:
            if not with_fields:
                with_fields = apiobj._default_fields

            query_fields = tools.listify(with_fields)
            query_fields = [x for x in query_fields if x not in ["labels"]]
            query_lines = [QUERY_FIELD_EXISTS(field=x) for x in query_fields]
            query = " and ".join(query_lines)

        if not fields:
            fields = apiobj._default_fields

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
class TestBoth(Base):
    """Pass."""

    def test__count_post_false(self, apiobj):
        """Pass."""
        data = apiobj._count(use_post=False)
        assert isinstance(data, tools.INT)

    def test__count_query_len_forces_post(self, apiobj):
        """Pass."""
        long_query = self.build_long_query(apiobj)

        data = apiobj._count(query=long_query, use_post=False)
        assert isinstance(data, tools.INT)

        response = apiobj._auth._http._LAST_RESPONSE
        assert response.request.method == "POST"

    def test__get_post_false(self, apiobj):
        """Pass."""
        data = apiobj._get(page_size=1, use_post=False)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], tools.LIST)
        assert len(data["assets"]) == 1
        assert isinstance(data["assets"][0], dict)

    def test__get_page_size_over_max(self, apiobj):
        """Pass."""
        data = apiobj._get(page_size=3000, use_post=False)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], tools.LIST)

        response = apiobj._auth._http._LAST_RESPONSE
        assert "limit=2000" in response.request.url

    def test__get_query_len_forces_post(self, apiobj):
        """Pass."""
        long_query = self.build_long_query(apiobj)
        fields = [apiobj.TEST_DATA["single_field"]["exp"]]

        data = apiobj._get(query=long_query, fields=fields, page_size=1, use_post=False)
        assert isinstance(data, dict)
        assert isinstance(data["assets"], tools.LIST)

        # 2.10 fixed use_post being ignored
        # total = data["page"]["totalResources"]
        # if total < constants.MAX_PAGE_SIZE:
        #     assert len(data["assets"]) == total
        # else:
        #     assert len(data["assets"]) == constants.MAX_PAGE_SIZE

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
        assert isinstance(data, tools.INT)

    def test_get(self, apiobj):
        """Pass."""
        data = apiobj.get(max_rows=1)
        assert isinstance(data, tools.LIST)
        assert len(data) == 1

    def test_get_maxpages(self, apiobj):
        """Pass."""
        data = apiobj.get(max_rows=22, max_pages=1)
        assert isinstance(data, tools.LIST)
        assert len(data) == 22

    def test_get_id(self, apiobj):
        """Pass."""
        asset = self.get_single_asset(apiobj=apiobj, fields=apiobj._default_fields)

        data = apiobj.get_by_id(id=asset["internal_axon_id"])
        assert isinstance(data, dict)
        assert data["internal_axon_id"] == asset["internal_axon_id"]

    def test_get_id_error(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get_by_id(id="badwolf")

    def test_count_by_saved_query(self, apiobj):
        """Pass."""
        sqs = apiobj.saved_query.get()
        sq = sqs[0]
        sq_name = sq["name"]
        data = apiobj.count_by_saved_query(name=sq_name)
        assert isinstance(data, tools.INT)

    def test_get_by_saved_query(self, apiobj):
        """Pass."""
        sqs = apiobj.saved_query.get()
        sq = sqs[0]
        sq_name = sq["name"]
        sq_fields = sq["view"]["fields"]
        data = apiobj.get_by_saved_query(name=sq_name, max_rows=1)
        last_get = apiobj._LAST_GET
        # 2.0.5: make sure the fields in sq are the ones that got supplied to the get
        assert last_get["fields"] == ",".join(sq_fields)
        assert isinstance(data, tools.LIST)

    def test_get_by_field_value(self, apiobj):
        """Pass."""
        asset = self.get_single_asset(apiobj=apiobj, fields=apiobj._default_fields)
        assert isinstance(asset, dict)
        field = apiobj.TEST_DATA["single_field"]["exp"]
        value = asset[field]

        assert value
        found = apiobj.get_by_value(
            value=value, field=field, fields=apiobj._default_fields, match_count=1
        )
        assert found[field] == value

    def test_get_by_field_value_list(self, apiobj):
        """Pass."""
        asset = self.get_single_asset(apiobj=apiobj, fields=apiobj._default_fields)
        assert isinstance(asset, dict)
        field = apiobj.TEST_DATA["single_field"]["exp"]
        value = asset[field]
        value_list = tools.listify(value)
        assert value
        found = apiobj.get_by_value(
            value=value_list, field=field, fields=apiobj._default_fields, match_count=1
        )
        found_value = found[field]

        assert tools.listify(found_value) == value_list

    def test_get_by_field_value_regex(self, apiobj):
        """Pass."""
        field = apiobj.TEST_DATA["single_field"]["exp"]
        value_re = "[a-zA-Z]"
        found = apiobj.get_by_value(
            value=value_re, value_regex=True, field=field, match_count=1, max_rows=1
        )
        assert isinstance(found, dict)
        assert any(
            [
                re.search(value_re, f)
                for f in tools.listify(obj=found[field], dictkeys=False)
            ]
        )

    def test_get_by_field_value_not(self, apiobj):
        """Pass."""
        count = apiobj.count()
        asset = self.get_single_asset(apiobj=apiobj, fields=apiobj._default_fields)
        assert isinstance(asset, dict)
        field = apiobj.TEST_DATA["single_field"]["exp"]

        asset_value = asset[field]
        found = apiobj.get_by_value(
            value=asset_value,
            value_not=True,
            field=field,
            fields=apiobj._default_fields,
            match_error=False,
        )
        assert isinstance(found, tools.LIST)
        assert len(found) == count - 1

    def test_get_by_field_value_match_error(self, apiobj):
        """Pass."""
        field = apiobj.TEST_DATA["single_field"]["exp"]
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get_by_value(
                value="BaDWoLf_8675309",
                field=field,
                match_count=1,
                max_rows=2,
                match_error=True,
            )


class Single(Base):
    """Pass."""

    def get_by_specifics(self, apiobj, specfield, specmethod):
        """Pass."""
        asset = self.get_single_asset(apiobj=apiobj, fields=specfield)
        asset_value = asset[specfield]
        value = tools.listify(obj=asset_value)[0]
        query_post = "and {}".format(QUERY_FIELD_EXISTS(field=specfield))
        found = getattr(apiobj, specmethod)(
            value=value, query_post=query_post, match_count=1, fields=specfield
        )
        assert isinstance(found, dict)
        found_value = found[specfield]
        assert tools.listify(found_value) == tools.listify(asset_value)


@pytest.mark.parametrize("apicls", [axonapi.api.Users], scope="class")
class TestUsers(Single):
    """Pass."""

    @pytest.mark.parametrize(
        "specfield,specmethod",
        [
            ["specific_data.data.username", "get_by_username"],
            ["specific_data.data.mail", "get_by_mail"],
        ],
        scope="class",
    )
    def test_get_by_specifics(self, apiobj, specfield, specmethod):
        """Pass."""
        self.get_by_specifics(apiobj=apiobj, specfield=specfield, specmethod=specmethod)


@pytest.mark.parametrize("apicls", [axonapi.api.Devices], scope="class")
class TestDevices(Single):
    """Pass."""

    @pytest.mark.parametrize(
        "specfield,specmethod",
        [
            ["specific_data.data.hostname", "get_by_hostname"],
            ["specific_data.data.network_interfaces.mac", "get_by_mac"],
            ["specific_data.data.network_interfaces.ips", "get_by_ip"],
        ],
        scope="class",
    )
    def test_get_by_specifics(self, apiobj, specfield, specmethod):
        """Pass."""
        self.get_by_specifics(apiobj=apiobj, specfield=specfield, specmethod=specmethod)

    def test_get_by_subnet(self, apiobj):
        """Pass."""
        specfield = "specific_data.data.network_interfaces.subnets"
        findfield = "specific_data.data.network_interfaces.ips"
        withfields = [findfield, specfield]
        asset = self.get_single_asset(
            apiobj=apiobj, with_fields=withfields, fields=withfields
        )
        assert specfield in asset, list(asset)
        asset_value = asset[specfield]

        value = tools.listify(obj=asset_value)[0]

        found = apiobj.get_by_subnet(
            value=value,
            max_rows=1,
            fields=findfield,
            query_post=" and {}".format(QUERY_FIELD_EXISTS(field=findfield)),
        )

        assert isinstance(found, tools.LIST)

        found_value = tools.listify(obj=found[0][findfield])[0]
        assert found_value == tools.listify(obj=asset[findfield], dictkeys=False)[0]

    def test_get_by_subnet_not(self, apiobj):
        """Pass."""
        specfield = "specific_data.data.network_interfaces.subnets"
        findfield = "specific_data.data.network_interfaces.ips"
        withfields = [findfield, specfield]
        asset = self.get_single_asset(
            apiobj=apiobj, with_fields=withfields, fields=withfields
        )
        assert specfield in asset, list(asset)
        asset_value = asset[specfield]

        value = tools.listify(obj=asset_value)[0]

        found = apiobj.get_by_subnet(
            value=value,
            value_not=True,
            max_rows=1,
            fields=findfield,
            query_post=" and {}".format(QUERY_FIELD_EXISTS(field=findfield)),
        )
        # could do value checking here, but we'd have to get every asset
        # lets not do that...
        assert isinstance(found, tools.LIST)


@pytest.mark.parametrize("apicls", [axonapi.api.Users, axonapi.Devices], scope="class")
class TestReports(Base):
    """Pass."""

    @pytest.fixture(scope="class")
    def report_data(self, apiobj):
        """Pass."""
        rows = apiobj.get(max_rows=20)
        assert isinstance(rows, tools.LIST)
        assert len(rows) == 20
        return rows

    def test_missing_adapters(self, apiobj, report_data):
        """Pass."""
        report = apiobj.reports.missing_adapters(rows=report_data)
        assert isinstance(report, tools.LIST)
        for item in report:
            assert isinstance(item, dict)
            assert isinstance(item["missing"], tools.LIST)
            assert isinstance(item["missing_nocnx"], tools.LIST)


@pytest.mark.parametrize("apicls", [axonapi.api.Users, axonapi.Devices], scope="class")
class TestFields(Base):
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

    def test_find_manual(self, apiobj):
        """Pass."""
        found = apiobj.fields.find(field="MANUAL:badwolf", all_fields=apiobj.ALL_FIELDS)
        assert found == "badwolf"

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
class TestLabels(Base):
    """Pass."""

    def test__get(self, apiobj):
        """Pass."""
        fields = apiobj.labels._get()
        assert isinstance(fields, tools.LIST)
        for x in fields:
            assert isinstance(x, tools.STR)

    def test_get(self, apiobj):
        """Pass."""
        fields = apiobj.labels._get()
        assert isinstance(fields, tools.LIST)
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
class TestSavedQuery(Base):
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

                # new in 2.10, unsure of
                # if not None, dict with keys: clearAll, selectAll, selectedValues
                filtered_adapters = qexpr.pop("filteredAdapters", {})

                assert isinstance(filtered_adapters, dict) or filtered_adapters is None
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

                    # new in 2.10, unsure of
                    # if not None, dict with keys: clearAll, selectAll, selectedValues
                    nfiltered_adapters = nested.pop("filteredAdapters", {})
                    assert (
                        isinstance(nfiltered_adapters, dict)
                        or nfiltered_adapters is None
                    )
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

    def test_get_maxpages(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get(max_pages=1, max_rows=1)
        assert isinstance(data, tools.LIST)
        assert len(data) == 1

    def test_get_empty(self, apiobj):
        """Pass."""
        query = 'name == "badwolf_notfound"'
        data = apiobj.saved_query.get(query=query)
        assert isinstance(data, tools.LIST)
        assert not data

    def test_get_by_id(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get()
        found = apiobj.saved_query.get_by_id(value=data[0]["uuid"])
        assert isinstance(found, dict)

    def test_get_by_id_notfound_noerr(self, apiobj):
        """Pass."""
        found = apiobj.saved_query.get_by_id(value="badwolf", match_error=False)
        assert found is None

    def test_get_by_id_notfound(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.saved_query.get_by_id(value="badwolf")

    def test_get_by_name(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get()
        found = apiobj.saved_query.get_by_name(value=data[0]["name"])
        assert isinstance(found, dict)

    def test_get_by_name_regex(self, apiobj):
        """Pass."""
        found = apiobj.saved_query.get_by_name(value=".*", value_regex=True)
        assert isinstance(found, tools.LIST)
        assert len(found) >= 1

    def test_get_by_name_notflag(self, apiobj):
        """Pass."""
        data = apiobj.saved_query.get()
        found = apiobj.saved_query.get_by_name(value=data[0]["name"], value_not=True)
        assert isinstance(found, tools.LIST)
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
        assert isinstance(got["assets"], tools.LIST)
        assert len(got["assets"]) == 1
        assert isinstance(got["assets"][0], dict)

        deleted = apiobj.saved_query._delete(ids=[added])
        assert not deleted

        re_got = apiobj.saved_query._get(query='name == "{}"'.format(name))
        assert isinstance(re_got, dict)
        assert isinstance(re_got["assets"], tools.LIST)
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
            apiobj.saved_query.get_by_name(name)

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
            apiobj.saved_query.get_by_name(name)

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
            apiobj.saved_query.get_by_name(name)


@pytest.mark.parametrize(
    "apicls", [(axonapi.api.Users), (axonapi.Devices)], scope="class"
)
class TestParsedFields(Base):
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
class TestRawFields(Base):
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
        assert isinstance(generic, tools.LIST)
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
