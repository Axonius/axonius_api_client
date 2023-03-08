# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.api import json_api
from axonius_api_client.constants.fields import Parsers
from axonius_api_client.exceptions import WizardError
from axonius_api_client.parsers.wizards import WizardParser


def patch_method(wizard_parser, monkeypatch, method, values):
    def mockery(*args, **kwargs):
        return values

    monkeypatch.setattr(wizard_parser, method, mockery)


class Base:
    @pytest.fixture(params=["api_devices", "api_users"])
    def wizard_parser(self, request):
        apiobj = request.getfixturevalue(request.param)
        obj = WizardParser(apiobj=apiobj)
        assert obj.apiobj == apiobj
        return obj


class TestMethods(Base):
    def test_parser_ops(self, wizard_parser):
        parsers = [x.value for x in Parsers]

        for parser in parsers:
            assert hasattr(wizard_parser, f"value_{parser}")

        for item in dir(wizard_parser):
            if item.startswith("value_") and callable(getattr(wizard_parser, item)):
                assert item[6:] in parsers

    def test_get_adapters(self, wizard_parser):
        items = wizard_parser.get_adapters()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, dict)

    def test_get_cnx_labels(self, wizard_parser):
        items = wizard_parser.get_cnx_labels()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, dict)

    def test_get_instances(self, wizard_parser):
        items = wizard_parser.get_instances()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, json_api.instances.Instance)

    def test_get_sqs(self, wizard_parser):
        items = wizard_parser.get_sqs()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, json_api.saved_queries.SavedQuery)

    def test_get_asset_tags(self, wizard_parser):
        items = wizard_parser.get_asset_tags()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, str)

    def test_get_asset_tags_expirable(self, wizard_parser):
        items = wizard_parser.get_asset_tags_expirable()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, str)


class Common:
    def test_empty(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="", parser=parser)


class TestToCsvAdapters(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_csv_adapters.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="  active_directory   ,   csv  ,,", parser=parser)
        assert ret == (
            '"active_directory_adapter", "csv_adapter"',
            "active_directory_adapter,csv_adapter",
        )

    def test_valid_list(self, wizard_parser, parser):
        ret = wizard_parser(value=["active_directory", "csv"], parser=parser)
        assert ret == (
            '"active_directory_adapter", "csv_adapter"',
            "active_directory_adapter,csv_adapter",
        )

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="badwolf", parser=parser)


class TestToCsvCnxLabel(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_csv_cnx_label.name

    def test_valid(self, core_node, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_cnx_labels",
            values=[
                {"label": "label1", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
                {"label": "label2", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
            ],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="label1, label2,", parser=parser)
        assert ret == ('"label1", "label2"', "label1,label2")

    def test_valid_list(self, core_node, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_cnx_labels",
            values=[
                {"label": "label1", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
                {"label": "label2", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
            ],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value=["label1", "label2"], parser=parser)
        assert ret == ('"label1", "label2"', "label1,label2")

    def test_invalid(self, core_node, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_cnx_labels",
            values=[
                {"label": "label1", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
                {"label": "label2", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
            ],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="label1, label3, label2,", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_cnx_labels", values=[], wizard_parser=wizard_parser, monkeypatch=monkeypatch
        )
        with pytest.raises(WizardError):
            wizard_parser(value="label1, label3, label2,", parser=parser)


class TestToCsvInt(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_csv_int.name

    def test_valid_int(self, wizard_parser, parser):
        ret = wizard_parser(value="1, 2, 3,", parser=parser)
        assert ret == ("1, 2, 3", "1,2,3")

    def test_valid_int_list(self, wizard_parser, parser):
        ret = wizard_parser(value=["1", "2", "3"], parser=parser)
        assert ret == ("1, 2, 3", "1,2,3")

    def test_valid_float(self, wizard_parser, parser):
        ret = wizard_parser(value="1.1, 2.3, 3.4,", parser=parser)
        assert ret == ("1.1, 2.3, 3.4", "1.1,2.3,3.4")

    def test_valid_float_list(self, wizard_parser, parser):
        ret = wizard_parser(value=["1.1", "2.3", "3.4"], parser=parser)
        assert ret == ("1.1, 2.3, 3.4", "1.1,2.3,3.4")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="1, 2, c", parser=parser)


class TestToCsvIp(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_csv_ip.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="192.168.1.28, 10.0.0.43, 10.4.2.1,", parser=parser)
        assert ret == (
            '"192.168.1.28", "10.0.0.43", "10.4.2.1"',
            "192.168.1.28,10.0.0.43,10.4.2.1",
        )

    def test_valid_list(self, wizard_parser, parser):
        ret = wizard_parser(value=["192.168.1.28", "10.0.0.43", "10.4.2.1"], parser=parser)
        assert ret == (
            '"192.168.1.28", "10.0.0.43", "10.4.2.1"',
            "192.168.1.28,10.0.0.43,10.4.2.1",
        )

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="192.168.1.0, 10.0.0", parser=parser)


class TestToCsvStr(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_csv_str.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="a, b, c,", parser=parser)
        assert ret == ('"a", "b", "c"', "a,b,c")

    def test_valid_list(self, wizard_parser, parser):
        ret = wizard_parser(value=["a", "b", "c"], parser=parser)
        assert ret == ('"a", "b", "c"', "a,b,c")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value=1, parser=parser)


class TestToCsvSubnet(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_csv_subnet.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="10.0.0.0/24, 192.168.1.0/24", parser=parser)
        assert ret == ('"10.0.0.0/24", "192.168.1.0/24"', "10.0.0.0/24,192.168.1.0/24")

    def test_valid_list(self, wizard_parser, parser):
        ret = wizard_parser(value=["10.0.0.0/24", "192.168.1.0/24"], parser=parser)
        assert ret == ('"10.0.0.0/24", "192.168.1.0/24"', "10.0.0.0/24,192.168.1.0/24")

    def test_invalid1(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="10.0.0.0", parser=parser)

    def test_invalid2(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="10.0.0/24", parser=parser)


class TestToCsvTags(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_csv_tags.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="tag1, tag2,", parser=parser)
        assert ret == ('"tag1", "tag2"', "tag1,tag2")

    def test_valid_list(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value=["tag1", "tag2"], parser=parser)
        assert ret == ('"tag1", "tag2"', "tag1,tag2")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="tag1, tag3, tag2,", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags", values=[], wizard_parser=wizard_parser, monkeypatch=monkeypatch
        )
        with pytest.raises(WizardError):
            wizard_parser(value="tag1, tag3, tag2,", parser=parser)


class TestToCsvTagsExpirable(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_csv_tags_expirable.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags_expirable",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="tag1, tag2,", parser=parser)
        assert ret == ('"tag1", "tag2"', "tag1,tag2")

    def test_valid_list(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags_expirable",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value=["tag1", "tag2"], parser=parser)
        assert ret == ('"tag1", "tag2"', "tag1,tag2")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags_expirable",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="tag1, tag3, tag2,", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags_expirable",
            values=[],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="tag1, tag3, tag2,", parser=parser)


class TestToStrDataScope(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self, api_data_scopes):
        if not api_data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")

        return Parsers.to_str_data_scope.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="enum_cb_data_scope",
            values="MOCK_UUID",
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="xxxx", parser=parser)
        assert ret == ("MOCK_UUID", "MOCK_UUID")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="I DO NOT EXISTSSSS", parser=parser)


class TestToStrSq(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_str_sq.name

    def test_valid_name(self, wizard_parser, monkeypatch, parser):
        sq = wizard_parser.apiobj.saved_query.get(as_dataclass=True)[0]
        ret = wizard_parser(value=f"{sq.name}", parser=parser)
        assert ret == (f"{sq.uuid}", f"{sq.uuid}")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="badwolf", parser=parser)


class TestToDt(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_dt.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="2020-09-06", parser=parser)
        assert ret == ("2020-09-06", "2020-09-06")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="x", parser=parser)


class TestToInSubnet(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_in_subnet.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="10.0.0.0/24", parser=parser)
        assert ret == (["167772160", "167772415"], "10.0.0.0/24")

    def test_invalid1(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="10.0.0.0", parser=parser)

    def test_invalid2(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="10.0.0/24", parser=parser)


class TestToInt(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_int.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="2", parser=parser)
        assert ret == ("2", 2)

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="x", parser=parser)


class TestToIp(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_ip.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="192.168.1.1", parser=parser)
        assert ret == ("192.168.1.1", "192.168.1.1")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="192.168.1", parser=parser)


class TestToNone(Base):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_none.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="2", parser=parser)
        assert ret == ("", None)


class TestToRawVersion(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_raw_version.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="82.6.2", parser=parser)
        assert ret == ("0000000820000000600000002", "82.6.2")

    def test_invalid1(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="82.6.2:boom", parser=parser)

    def test_invalid2(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="82.6.b", parser=parser)


class TestToStr(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_str.name

    def test_valid_enum(self, wizard_parser, parser):
        ret = wizard_parser(value="abc", enum=["abc"], parser=parser)
        assert ret == ("abc", "abc")

    def test_valid_enum_items(self, wizard_parser, parser):
        ret = wizard_parser(value="abc", enum_items=["abc"], parser=parser)
        assert ret == ("abc", "abc")

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="2", parser=parser)
        assert ret == ("2", "2")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value=2, parser=parser)

    def test_invalid_enum(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="def", enum=["abc"], parser=parser)

    def test_invalid_enum_items(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="def", enum_items=["abc"], parser=parser)

    def test_bad_enum(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="def", enum={"k": "v"}, parser=parser)

    def test_bad_enum_items(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="def", enum_items={"k": "v"}, parser=parser)


class TestToStrAdapters(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_str_adapters.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="active_directory", parser=parser)
        assert ret == ("active_directory_adapter", "active_directory_adapter")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="badwolf", parser=parser)


class TestToStrCnxLabel(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_str_cnx_label.name

    def test_valid(self, core_node, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_cnx_labels",
            values=[
                {"label": "label1", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
                {"label": "label2", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
            ],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="label1", parser=parser)
        assert ret == ("label1", "label1")

    def test_invalid(self, core_node, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_cnx_labels",
            values=[
                {"label": "label1", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
                {"label": "label2", "plugin_name": "csv_adapter", "node_id": core_node["id"]},
            ],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="label3", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_cnx_labels", values=[], wizard_parser=wizard_parser, monkeypatch=monkeypatch
        )
        with pytest.raises(WizardError):
            wizard_parser(value="label1", parser=parser)


class TestToStrEscapedRegex(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_str_escaped_regex.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="test.domain", parser=parser)
        assert ret == ("test\\.domain", "test.domain")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value=2, parser=parser)


class TestToStrTags(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_str_tags.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="tag1", parser=parser)
        assert ret == ("tag1", "tag1")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="tag3", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags", values=[], wizard_parser=wizard_parser, monkeypatch=monkeypatch
        )
        with pytest.raises(WizardError):
            wizard_parser(value="tag1", parser=parser)


class TestToStrTagsExpirable(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_str_tags_expirable.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags_expirable",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="tag1", parser=parser)
        assert ret == ("tag1", "tag1")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags_expirable",
            values=["tag1", "tag2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="tag3", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_method(
            method="get_asset_tags_expirable",
            values=[],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="tag1", parser=parser)


class TestToStrSubnet(Base, Common):
    @pytest.fixture(scope="class")
    def parser(self):
        return Parsers.to_str_subnet.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="10.0.0.0/24", parser=parser)
        assert ret == ("10.0.0.0/24", "10.0.0.0/24")

    def test_invalid1(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="10.0.0.0", parser=parser)

    def test_invalid2(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="10.0.0/24", parser=parser)
