# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.wizard.wizard"""
import pytest
from axonius_api_client.api.parsers.constants import Operators
from axonius_api_client.constants import ALL_NAME
from axonius_api_client.exceptions import NotFoundError, WizardError
from axonius_api_client.wizard import ValueParser, Wizard
from axonius_api_client.wizard.constants import Entry, Types


class TestWizard:
    @pytest.fixture(params=["api_devices", "api_users"])
    def wizard(self, request):
        apiobj = request.getfixturevalue(request.param)
        obj = Wizard(apiobj=apiobj)
        assert obj._apiobj == apiobj
        assert isinstance(obj._value_parser, ValueParser)
        return obj


class TestCheckEntryType(TestWizard):
    def test_invalid(self, wizard):
        with pytest.raises(WizardError) as exc:
            wizard._check_entry_type(entry={Entry.TYPE: "badwolf"}, types=Types.DICT)
        assert "Invalid type" in str(exc.value)

    def test_valid(self, wizard):
        ret = wizard._check_entry_type(
            entry={Entry.TYPE: Types.DICT[0].upper()}, types=Types.DICT
        )
        assert ret == Types.DICT[0]


class TestGetField(TestWizard):
    def test_invalid_agg(self, wizard):
        field = ALL_NAME
        with pytest.raises(WizardError) as exc:
            wizard._get_field(value=field, value_raw=f"{field} blah blah")
        assert "Can not use" in str(exc)

    def test_invalid(self, wizard):
        field = "badwolf"
        with pytest.raises(WizardError) as exc:
            wizard._get_field(value=field, value_raw=f"{field} blah blah")
        assert "Unable to find FIELD" in str(exc)

    def test_valid(self, wizard):
        field = wizard._apiobj.FIELD_SIMPLE
        ret = wizard._get_field(value=field, value_raw=f"{field} blah blah")
        assert ret["name_qual"] == field


class TestGetFieldComplex(TestWizard):
    @pytest.mark.parametrize(
        "field, value_raw, exc_str",
        [
            [ALL_NAME, f"{ALL_NAME} blah blah", "Can not use"],
            ["badwolf", "badwolf blah blah", "Unable to find COMPLEX-FIELD"],
            ["internal_axon_id", "internal_axon_id blah blah", "Invalid COMPLEX-FIELD"],
        ],
    )
    def test_invalid(self, wizard, field, value_raw, exc_str):
        with pytest.raises(WizardError) as exc:
            wizard._get_field_complex(value=field, value_raw=value_raw)
        assert exc_str in str(exc)

    def test_valid(self, wizard):
        field = wizard._apiobj.FIELD_COMPLEX
        ret = wizard._get_field_complex(value=field, value_raw=f"{field} blah blah")
        assert ret["name_qual"] == field


class TestGetOperator(TestWizard):
    def test_valid(self, wizard):
        field = {
            "type": "string",
            "name_qual": "badwolf",
            "name": "badwolf",
            "parent": "moo",
        }
        ret = wizard._get_operator(field=field, operator="equals", value_raw="boom")
        assert ret == Operators.equals_str

    def test_invalid(self, wizard):
        field = {
            "type": "string",
            "name_qual": "badwolf",
            "name": "badwolf",
            "parent": "moo",
        }
        with pytest.raises(NotFoundError) as exc:
            wizard._get_operator(field=field, operator="xx", value_raw="boom")
        assert "Invalid OPERATOR name" in str(exc.value)


class TestCheckEntryKeys(TestWizard):
    @pytest.mark.parametrize(
        "entry, keys, exc_str",
        [
            [
                {Entry.TYPE: "badwolf"},
                Entry.REQ,
                f"Missing required key {Entry.VALUE!r}",
            ],
            [
                {Entry.TYPE: "", Entry.VALUE: "y"},
                Entry.REQ,
                f"Empty required key {Entry.TYPE!r}",
            ],
            [{Entry.TYPE: 1, Entry.VALUE: "y"}, Entry.REQ, "Invalid type "],
        ],
    )
    def test_invalid(self, wizard, entry, keys, exc_str):
        with pytest.raises(WizardError) as exc:
            wizard._check_entry_keys(entry=entry, keys=keys)
        assert exc_str in str(exc.value)

    def test_valid(self, wizard):
        ret = wizard._check_entry_type(
            entry={Entry.TYPE: Types.DICT[0].upper()}, types=Types.DICT
        )
        assert ret == Types.DICT[0]


class TestSplitFlags(TestWizard):
    @pytest.mark.parametrize(
        "value_raw, exp",
        [
            [
                "! @ $ hostname contains blah  )",
                (["!", "@", "$", ")"], "hostname contains blah "),
            ],
            [
                " ! & hostname contains blah )",
                (["!", "&", ")"], "hostname contains blah"),
            ],
            [
                "!|hostname contains blah)",
                (["!", "|", ")"], "hostname contains blah"),
            ],
            [
                "hostname contains blah",
                ([], "hostname contains blah"),
            ],
            [
                "hostname contains blah ",
                ([], "hostname contains blah "),
            ],
            [
                "hostname contains blah s2904829 50(#*)$(!*&_)(@!",
                ([], "hostname contains blah s2904829 50(#*)$(!*&_)(@!"),
            ],
        ],
    )
    def test_valid(self, wizard, value_raw, exp):
        ret = wizard._split_flags(value_raw=value_raw)
        assert ret == exp

    @pytest.mark.parametrize(
        "value_raw",
        ["#@#$"],
    )
    def test_invalid(self, wizard, value_raw):
        with pytest.raises(WizardError):
            wizard._split_flags(value_raw=value_raw)


class TestSplitSimple(TestWizard):
    @pytest.mark.parametrize(
        "value_raw, exp",
        [
            [
                "badwolf equals fool",
                ("badwolf", "equals", "fool"),
            ],
            [
                "badwolf equals fool it up",
                ("badwolf", "equals", "fool it up"),
            ],
            [
                "badwolf equals",
                ("badwolf", "equals", ""),
            ],
            [
                "badwolf_moo.foo equals",
                ("badwolf_moo.foo", "equals", ""),
            ],
        ],
    )
    def test_valid(self, wizard, value_raw, exp):
        ret = wizard._split_simple(value_raw=value_raw)
        assert ret == exp

    @pytest.mark.parametrize(
        "value_raw, exc_str",
        [
            ["", "FIELD"],
            ["!ab@ contains blah", "FIELD"],
            ["badwolf", "OPERATOR"],
            ["badwolf 232 blah", "OPERATOR"],
        ],
    )
    def test_invalid(self, wizard, value_raw, exc_str):
        with pytest.raises(WizardError) as exc:
            wizard._split_simple(value_raw=value_raw)
        assert exc_str in str(exc.value)


class TestSplitComplex(TestWizard):
    @pytest.mark.parametrize(
        "value_raw, exp",
        [
            [
                "badwolf // subfield contains blah",
                ("badwolf", ["subfield contains blah"]),
            ],
            [
                "badwolf // subfield contains blah // subfield contains moo",
                ("badwolf", ["subfield contains blah", "subfield contains moo"]),
            ],
            [
                "badwolf_moo.foo // subfield contains blah // subfield contains moo",
                (
                    "badwolf_moo.foo",
                    ["subfield contains blah", "subfield contains moo"],
                ),
            ],
        ],
    )
    def test_valid(self, wizard, value_raw, exp):
        ret = wizard._split_complex(value_raw=value_raw)
        assert ret == exp

    @pytest.mark.parametrize(
        "value_raw, exc_str",
        [
            ["", f"No {Entry.CSPLIT} found in value"],
            ["badwolf", f"No {Entry.CSPLIT} found in value"],
            ["!ab@ // subfield contains blah", "FIELD"],
        ],
    )
    def test_invalid(self, wizard, value_raw, exc_str):
        with pytest.raises(WizardError) as exc:
            wizard._split_complex(value_raw=value_raw)
        assert exc_str in str(exc.value)
