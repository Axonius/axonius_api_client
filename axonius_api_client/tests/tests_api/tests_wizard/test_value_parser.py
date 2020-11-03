# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.constants.fields import Parsers
from axonius_api_client.exceptions import WizardError
from axonius_api_client.parsers.wizards import WizardParser


def patch_cnx_labels(wizard_parser, monkeypatch, values):
    def _mock(*args, **kwargs):
        return values

    monkeypatch.setattr(wizard_parser, "_cnx_labels", _mock)


def patch_tags(wizard_parser, monkeypatch, values):
    def _mock(*args, **kwargs):
        return values

    monkeypatch.setattr(wizard_parser, "_tags", _mock)


class TestWizardParser:
    @pytest.fixture(params=["api_devices", "api_users"])
    def wizard_parser(self, request):
        apiobj = request.getfixturevalue(request.param)
        obj = WizardParser(apiobj=apiobj)
        assert obj.apiobj == apiobj
        return obj

    def test_parser_ops(self, wizard_parser):
        parsers = [x.value for x in Parsers]

        for parser in parsers:
            assert hasattr(wizard_parser, f"value_{parser}")

        for item in dir(wizard_parser):
            if item.startswith("value_") and callable(getattr(wizard_parser, item)):
                assert item[6:] in parsers

    def test_api_items(self, wizard_parser):
        assert isinstance(wizard_parser._tags(), list)
        for tag in wizard_parser._tags():
            assert isinstance(tag, str)

        assert isinstance(wizard_parser._adapters(), list)
        for adapter in wizard_parser._adapters():
            assert isinstance(adapter, dict)

        assert isinstance(wizard_parser._adapter_names(), dict)
        for k, v in wizard_parser._adapter_names().items():
            assert isinstance(k, str)
            assert isinstance(v, str)

        assert isinstance(wizard_parser._cnx_labels(), list)
        for label in wizard_parser._cnx_labels():
            assert isinstance(label, str)


class Common:
    def test_empty(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="", parser=parser)


class TestToCsvAdapters(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_adapters.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="  active_directory   ,   aws  ,,", parser=parser)
        assert ret == (
            '"active_directory_adapter", "aws_adapter"',
            "active_directory_adapter,aws_adapter",
        )

    def test_valid_list(self, wizard_parser, parser):
        ret = wizard_parser(value=["active_directory", "aws"], parser=parser)
        assert ret == (
            '"active_directory_adapter", "aws_adapter"',
            "active_directory_adapter,aws_adapter",
        )

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="badwolf", parser=parser)


class TestToCsvCnxLabel(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_cnx_label.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="label1, label2,", parser=parser)
        assert ret == ('"label1", "label2"', "label1,label2")

    def test_valid_list(self, wizard_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value=["label1", "label2"], parser=parser)
        assert ret == ('"label1", "label2"', "label1,label2")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="label1, label3, label2,", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_cnx_labels(values=[], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            wizard_parser(value="label1, label3, label2,", parser=parser)


class TestToCsvInt(TestWizardParser, Common):
    @pytest.fixture
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


class TestToCsvIp(TestWizardParser, Common):
    @pytest.fixture
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


class TestToCsvStr(TestWizardParser, Common):
    @pytest.fixture
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


class TestToCsvSubnet(TestWizardParser, Common):
    @pytest.fixture
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


class TestToCsvTags(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_csv_tags.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        ret = wizard_parser(value="tag1, tag2,", parser=parser)
        assert ret == ('"tag1", "tag2"', "tag1,tag2")

    def test_valid_list(self, wizard_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        ret = wizard_parser(value=["tag1", "tag2"], parser=parser)
        assert ret == ('"tag1", "tag2"', "tag1,tag2")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            wizard_parser(value="tag1, tag3, tag2,", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_tags(values=[], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            wizard_parser(value="tag1, tag3, tag2,", parser=parser)


class TestToDt(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_dt.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="2020-09-06", parser=parser)
        assert ret == ("2020-09-06", "2020-09-06")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="x", parser=parser)


class TestToInSubnet(TestWizardParser, Common):
    @pytest.fixture
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


class TestToInt(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_int.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="2", parser=parser)
        assert ret == ("2", 2)

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="x", parser=parser)


class TestToIp(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_ip.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="192.168.1.1", parser=parser)
        assert ret == ("192.168.1.1", "192.168.1.1")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="192.168.1", parser=parser)


class TestToNone(TestWizardParser):
    @pytest.fixture
    def parser(self):
        return Parsers.to_none.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="2", parser=parser)
        assert ret == ("", None)


class TestToRawVersion(TestWizardParser, Common):
    @pytest.fixture
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


class TestToStr(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="2", parser=parser)
        assert ret == ("2", "2")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value=2, parser=parser)


class TestToStrAdapters(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_adapters.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="active_directory", parser=parser)
        assert ret == ("active_directory_adapter", "active_directory_adapter")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value="badwolf", parser=parser)


class TestToStrCnxLabel(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_cnx_label.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        ret = wizard_parser(value="label1", parser=parser)
        assert ret == ("label1", "label1")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        patch_cnx_labels(
            values=["label1", "label2"],
            wizard_parser=wizard_parser,
            monkeypatch=monkeypatch,
        )
        with pytest.raises(WizardError):
            wizard_parser(value="label3", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_cnx_labels(values=[], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            wizard_parser(value="label1", parser=parser)


class TestToStrEscapedRegex(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_escaped_regex.name

    def test_valid(self, wizard_parser, parser):
        ret = wizard_parser(value="test.domain", parser=parser)
        assert ret == ("test\\.domain", "test.domain")

    def test_invalid(self, wizard_parser, parser):
        with pytest.raises(WizardError):
            wizard_parser(value=2, parser=parser)


class TestToStrTags(TestWizardParser, Common):
    @pytest.fixture
    def parser(self):
        return Parsers.to_str_tags.name

    def test_valid(self, wizard_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        ret = wizard_parser(value="tag1", parser=parser)
        assert ret == ("tag1", "tag1")

    def test_invalid(self, wizard_parser, monkeypatch, parser):
        patch_tags(values=["tag1", "tag2"], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            wizard_parser(value="tag3", parser=parser)

    def test_no_items(self, wizard_parser, monkeypatch, parser):
        patch_tags(values=[], wizard_parser=wizard_parser, monkeypatch=monkeypatch)
        with pytest.raises(WizardError):
            wizard_parser(value="tag1", parser=parser)


class TestToStrSubnet(TestWizardParser, Common):
    @pytest.fixture
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
