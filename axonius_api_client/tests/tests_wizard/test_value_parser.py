# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.api.parsers.constants import Parsers
from axonius_api_client.exceptions import WizardError
from axonius_api_client.wizard import ValueParser


def patch_cnx_labels(value_parser, monkeypatch, values):
    def _mock(*args, **kwargs):
        return values

    monkeypatch.setattr(value_parser, "_cnx_labels", _mock)


def patch_tags(value_parser, monkeypatch, values):
    def _mock(*args, **kwargs):
        return values

    monkeypatch.setattr(value_parser, "_tags", _mock)


class TestValueParser:
    @pytest.fixture(params=["api_devices", "api_users"])
    def value_parser(self, request):
        apiobj = request.getfixturevalue(request.param)
        obj = ValueParser(apiobj=apiobj)
        assert obj.apiobj == apiobj
        return obj

    def test_parser_ops(self, value_parser):
        parsers = [x.value for x in Parsers]

        for parser in parsers:
            assert hasattr(value_parser, f"value_{parser}")

        for item in dir(value_parser):
            if item.startswith("value_") and callable(getattr(value_parser, item)):
                assert item[6:] in parsers

    def test_api_items(self, value_parser):
        assert isinstance(value_parser._tags(), list)
        for tag in value_parser._tags():
            assert isinstance(tag, str)

        assert isinstance(value_parser._adapters(), list)
        for adapter in value_parser._adapters():
            assert isinstance(adapter, dict)

        assert isinstance(value_parser._adapter_names(), dict)
        for k, v in value_parser._adapter_names().items():
            assert isinstance(k, str)
            assert isinstance(v, str)

        assert isinstance(value_parser._cnx_labels(), list)
        for label in value_parser._cnx_labels():
            assert isinstance(label, str)


class Common:
    def test_empty(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="", parser=parser)


class TestToCsvAdapters(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_adapters.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="  active_directory   ,   aws  ,,", parser=parser)
        assert ret == (
            '"active_directory_adapter", "aws_adapter"',
            "active_directory_adapter,aws_adapter",
        )

    def test_valid_list(self, value_parser, parser):
        ret = value_parser(value=["active_directory", "aws"], parser=parser)
        assert ret == (
            '"active_directory_adapter", "aws_adapter"',
            "active_directory_adapter,aws_adapter",
        )

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="badwolf", parser=parser)


class TestToCsvCnxLabel(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_cnx_label.name

    def test_valid(self, value_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            value_parser=value_parser,
            monkeypatch=monkeypatch,
        )
        ret = value_parser(value="label1, label2,", parser=parser)
        assert ret == ('"label1", "label2"', "label1,label2")

    def test_valid_list(self, value_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            value_parser=value_parser,
            monkeypatch=monkeypatch,
        )
        ret = value_parser(value=["label1", "label2"], parser=parser)
        assert ret == ('"label1", "label2"', "label1,label2")

    def test_invalid(self, value_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            value_parser=value_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            value_parser(value="label1, label3, label2,", parser=parser)

    def test_no_items(self, value_parser, monkeypatch, parser):
        patch_cnx_labels(values=[], value_parser=value_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            value_parser(value="label1, label3, label2,", parser=parser)


class TestToCsvInt(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_int.name

    def test_valid_int(self, value_parser, parser):
        ret = value_parser(value="1, 2, 3,", parser=parser)
        assert ret == ("1, 2, 3", "1,2,3")

    def test_valid_int_list(self, value_parser, parser):
        ret = value_parser(value=["1", "2", "3"], parser=parser)
        assert ret == ("1, 2, 3", "1,2,3")

    def test_valid_float(self, value_parser, parser):
        ret = value_parser(value="1.1, 2.3, 3.4,", parser=parser)
        assert ret == ("1.1, 2.3, 3.4", "1.1,2.3,3.4")

    def test_valid_float_list(self, value_parser, parser):
        ret = value_parser(value=["1.1", "2.3", "3.4"], parser=parser)
        assert ret == ("1.1, 2.3, 3.4", "1.1,2.3,3.4")

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="1, 2, c", parser=parser)


class TestToCsvIp(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_ip.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="192.168.1.28, 10.0.0.43, 10.4.2.1,", parser=parser)
        assert ret == (
            '"192.168.1.28", "10.0.0.43", "10.4.2.1"',
            "192.168.1.28,10.0.0.43,10.4.2.1",
        )

    def test_valid_list(self, value_parser, parser):
        ret = value_parser(value=["192.168.1.28", "10.0.0.43", "10.4.2.1"], parser=parser)
        assert ret == (
            '"192.168.1.28", "10.0.0.43", "10.4.2.1"',
            "192.168.1.28,10.0.0.43,10.4.2.1",
        )

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="192.168.1.0, 10.0.0", parser=parser)


class TestToCsvStr(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_str.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="a, b, c,", parser=parser)
        assert ret == ('"a", "b", "c"', "a,b,c")

    def test_valid_list(self, value_parser, parser):
        ret = value_parser(value=["a", "b", "c"], parser=parser)
        assert ret == ('"a", "b", "c"', "a,b,c")

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value=1, parser=parser)


class TestToCsvSubnet(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_subnet.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="10.0.0.0/24, 192.168.1.0/24", parser=parser)
        assert ret == ('"10.0.0.0/24", "192.168.1.0/24"', "10.0.0.0/24,192.168.1.0/24")

    def test_valid_list(self, value_parser, parser):
        ret = value_parser(value=["10.0.0.0/24", "192.168.1.0/24"], parser=parser)
        assert ret == ('"10.0.0.0/24", "192.168.1.0/24"', "10.0.0.0/24,192.168.1.0/24")

    def test_invalid1(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="10.0.0.0", parser=parser)

    def test_invalid2(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="10.0.0/24", parser=parser)


class TestToCsvTags(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_tags.name

    def test_valid(self, value_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], value_parser=value_parser, monkeypatch=monkeypatch)
        ret = value_parser(value="tag1, tag2,", parser=parser)
        assert ret == ('"tag1", "tag2"', "tag1,tag2")

    def test_valid_list(self, value_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], value_parser=value_parser, monkeypatch=monkeypatch)
        ret = value_parser(value=["tag1", "tag2"], parser=parser)
        assert ret == ('"tag1", "tag2"', "tag1,tag2")

    def test_invalid(self, value_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], value_parser=value_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            value_parser(value="tag1, tag3, tag2,", parser=parser)

    def test_no_items(self, value_parser, monkeypatch, parser):
        patch_tags(values=[], value_parser=value_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            value_parser(value="tag1, tag3, tag2,", parser=parser)


class TestToDt(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_dt.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="2020-09-06", parser=parser)
        assert ret == ("2020-09-06", "2020-09-06")

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="x", parser=parser)


class TestToInSubnet(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_in_subnet.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="10.0.0.0/24", parser=parser)
        assert ret == (["167772160", "167772415"], "10.0.0.0/24")

    def test_invalid1(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="10.0.0.0", parser=parser)

    def test_invalid2(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="10.0.0/24", parser=parser)


class TestToInt(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_int.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="2", parser=parser)
        assert ret == ("2", 2)

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="x", parser=parser)


class TestToIp(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_ip.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="192.168.1.1", parser=parser)
        assert ret == ("192.168.1.1", "192.168.1.1")

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="192.168.1", parser=parser)


class TestToNone(TestValueParser):
    @pytest.fixture
    def parser(self):
        return Parsers.to_none.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="2", parser=parser)
        assert ret == ("", None)


class TestToRawVersion(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_raw_version.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="82.6.2", parser=parser)
        assert ret == ("0000000820000000600000002", "82.6.2")

    def test_invalid1(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="82.6.2:boom", parser=parser)

    def test_invalid2(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="82.6.b", parser=parser)


class TestToStr(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="2", parser=parser)
        assert ret == ("2", "2")

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value=2, parser=parser)


class TestToStrAdapters(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_adapters.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="active_directory", parser=parser)
        assert ret == ("active_directory_adapter", "active_directory_adapter")

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="badwolf", parser=parser)


class TestToStrCnxLabel(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_cnx_label.name

    def test_valid(self, value_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            value_parser=value_parser,
            monkeypatch=monkeypatch,
        )
        ret = value_parser(value="label1", parser=parser)
        assert ret == ("label1", "label1")

    def test_invalid(self, value_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            value_parser=value_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            value_parser(value="label3", parser=parser)

    def test_no_items(self, value_parser, monkeypatch, parser):
        patch_cnx_labels(values=[], value_parser=value_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            value_parser(value="label1", parser=parser)


class TestToStrEscapedRegex(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_escaped_regex.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="test.domain", parser=parser)
        assert ret == ("test\\.domain", "test.domain")

    def test_invalid(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value=2, parser=parser)


class TestToStrTags(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_tags.name

    def test_valid(self, value_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], value_parser=value_parser, monkeypatch=monkeypatch)
        ret = value_parser(value="tag1", parser=parser)
        assert ret == ("tag1", "tag1")

    def test_invalid(self, value_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], value_parser=value_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            value_parser(value="tag3", parser=parser)

    def test_no_items(self, value_parser, monkeypatch, parser):
        patch_tags(values=[], value_parser=value_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            value_parser(value="tag1", parser=parser)


class TestToStrSubnet(TestValueParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_subnet.name

    def test_valid(self, value_parser, parser):
        ret = value_parser(value="10.0.0.0/24", parser=parser)
        assert ret == ("10.0.0.0/24", "10.0.0.0/24")

    def test_invalid1(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="10.0.0.0", parser=parser)

    def test_invalid2(self, value_parser, parser):
        with pytest.raises(WizardError):
            value_parser(value="10.0.0/24", parser=parser)
