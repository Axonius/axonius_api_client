# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.query_wizard."""

import pytest

from axonius_api_client.api.wizards import WizardText
from axonius_api_client.constants.wizards import Entry, Results, Types
from axonius_api_client.exceptions import WizardError
from axonius_api_client.parsers.wizards import WizardParser

from .test_wizard import TestData


class TestWizardText:
    @pytest.fixture(params=["api_devices", "api_users"])
    def wizard(self, request):
        apiobj = request.getfixturevalue(request.param)
        obj = WizardText(apiobj=apiobj)
        assert obj.APIOBJ == apiobj
        assert isinstance(obj.PARSER, WizardParser)
        return obj


class TestLineToEntry(TestWizardText):
    def test_valid(self, wizard):
        line = f"{Types.SIMPLE} field"
        src = "boom"
        exp = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "field",
            Entry.SRC: src,
            Entry.FLAGS: [],
        }
        ret = wizard._line_to_entry(line=line, src=src)
        assert ret == exp

    def test_invalid(self, wizard):
        line = f"{Types.SIMPLE}"
        src = "boom"
        with pytest.raises(WizardError) as exc:
            wizard._line_to_entry(line=line, src=src)
        assert "Must supply a filter after type" in str(exc.value)


class TestLinesToEntries(TestWizardText):
    def test_valid(self, wizard):
        line1 = f"{Types.SIMPLE}    field equals boom"
        line2 = f"{Types.COMPLEX} field // sub1 contains boom // sub2 equals blah"
        lines = [line1, line2, "", "   # another boom", "# BOOM"]
        content = "\n".join(lines)
        source = "test str"
        exp = [
            {
                Entry.TYPE: Types.SIMPLE,
                Entry.VALUE: "field equals boom",
                Entry.SRC: f"{source} line #1: {line1}",
                Entry.FLAGS: [],
            },
            {
                Entry.TYPE: Types.COMPLEX,
                Entry.VALUE: "field // sub1 contains boom // sub2 equals blah",
                Entry.SRC: f"{source} line #2: {line2}",
                Entry.FLAGS: [],
            },
        ]
        ret = wizard._lines_to_entries(content=content, source=source)
        assert ret == exp

    def test_invalid(self, wizard):
        line1 = f"{Types.SIMPLE} field equals boom"
        line2 = f"{Types.COMPLEX}"
        lines = [line1, line2, "", "   # another boom", "# BOOM"]
        content = "\n".join(lines)
        source = "test str"
        with pytest.raises(WizardError) as exc:
            wizard._lines_to_entries(content=content, source=source)
        assert "Error parsing from" in str(exc.value)
        assert "Must supply a filter after type" in str(exc.value)


class TestParse(TestWizardText, TestData):
    def test_valid(self, wizard, test_data1):
        simple = wizard.APIOBJ.FIELD_SIMPLE
        cplex = wizard.APIOBJ.FIELD_COMPLEX
        sub = wizard.APIOBJ.FIELD_COMPLEX_SUB

        line1_value = f"{simple} exists"
        line1 = f"{Types.SIMPLE} {line1_value}"
        line2_value = f"{simple} contains test"
        line2 = f"{Types.SIMPLE} {line2_value}"
        line3_value = f"|{simple} contains dev"
        line3 = f"{Types.SIMPLE} {line3_value}"

        line4_value = f"{cplex} exists"
        line4 = f"{Types.SIMPLE} {line4_value}"
        line5_value = f"!{cplex} // {sub} contains boom"
        line5 = f"{Types.COMPLEX} {line5_value}"

        lines = [line1, line2, line3, line4, line5, "", "   # another boom", "# BOOM"]
        content = "\n".join(lines)
        _, exp_exprs, exp_query = test_data1

        ret = wizard.parse(content=content)
        assert ret[Results.QUERY] == exp_query
        assert ret[Results.EXPRS] == exp_exprs


class TestParsePath(TestWizardText, TestData):
    def test_valid(self, wizard, test_data1, tmp_path):
        path = tmp_path / "test.txt"

        simple = wizard.APIOBJ.FIELD_SIMPLE
        cplex = wizard.APIOBJ.FIELD_COMPLEX
        sub = wizard.APIOBJ.FIELD_COMPLEX_SUB

        line1_value = f"{simple} exists"
        line1 = f"{Types.SIMPLE} {line1_value}"
        line2_value = f"{simple} contains test"
        line2 = f"{Types.SIMPLE} {line2_value}"
        line3_value = f"|{simple} contains dev"
        line3 = f"{Types.SIMPLE} {line3_value}"

        line4_value = f"{cplex} exists"
        line4 = f"{Types.SIMPLE} {line4_value}"
        line5_value = f"!{cplex} // {sub} contains boom"
        line5 = f"{Types.COMPLEX} {line5_value}"

        lines = [line1, line2, line3, line4, line5, "", "   # another boom", "# BOOM"]
        content = "\n".join(lines)
        path.write_text(content)
        _, exp_exprs, exp_query = test_data1

        ret = wizard.parse_path(path=path)
        assert ret[Results.QUERY] == exp_query
        assert ret[Results.EXPRS] == exp_exprs
