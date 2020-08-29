# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.query_wizard."""
import pytest
from axonius_api_client.data_classes.wizard import ExprKeys, TextTypes
from axonius_api_client.exceptions import ToolsError, WizardError
from axonius_api_client.query_wizard import WizardText


class TestWizardText:
    """Test ParserUrl."""

    def test_from_path(self, tmp_path):
        content = f"""
{ExprKeys.FIELD}=last_seen, {ExprKeys.OP}=last_hours, {ExprKeys.VALUE}=24
"""
        test_path = tmp_path / "badwolf.text"
        test_path.write_text(content)

        lines = content.splitlines()
        exp = [
            {
                ExprKeys.FIELD: "last_seen",
                ExprKeys.IDX: 1,
                ExprKeys.OP: "last_hours",
                ExprKeys.SRC: {ExprKeys.SRC_LINE: lines[1], ExprKeys.SRC_LINE_NUM: 2},
                ExprKeys.TYPE: TextTypes.simple.name_expr,
                ExprKeys.VALUE: "24",
            }
        ]

        content = "\n".join(lines)
        text_wizard = WizardText()
        exprs = text_wizard.from_path(path=test_path)

        assert exprs == exp

    def test_from_text_err(self):
        content = f"{ExprKeys.TYPE}=badwolf"
        text_wizard = WizardText()
        with pytest.raises(WizardError) as excinfo:
            text_wizard.from_text(content=content)
        assert str(excinfo.value).startswith("Error while parsing expression ")

    def test_from_text_bracket(self):
        content = f"""
{ExprKeys.TYPE}={TextTypes.start_bracket.name_text}
    {ExprKeys.FIELD}=last_seen, {ExprKeys.OP}=last_hours, {ExprKeys.VALUE}=24
    {ExprKeys.TYPE} = {TextTypes.start_complex.name_text.upper()}, {ExprKeys.LOG} = and, {ExprKeys.FIELD}=agg:installed_software
        {ExprKeys.SUB}=name, {ExprKeys.OP}=equals, {ExprKeys.VALUE}="Google Chrome"
        {ExprKeys.SUB}=version, {ExprKeys.OP}=less_than, {ExprKeys.VALUE}=99
    {ExprKeys.TYPE}={TextTypes.stop_complex.name_text}
{ExprKeys.TYPE}={TextTypes.stop_bracket.name_text}
{ExprKeys.FIELD}=last_seen, {ExprKeys.OP}=last_hours, {ExprKeys.VALUE}=24
"""  # noqa
        lines = content.splitlines()
        exp = [
            {
                ExprKeys.IDX: 1,
                ExprKeys.SRC: {ExprKeys.SRC_LINE: lines[1], ExprKeys.SRC_LINE_NUM: 2},
                ExprKeys.SUBS: [
                    {
                        ExprKeys.FIELD: "last_seen",
                        ExprKeys.IDX: 2,
                        ExprKeys.OP: "last_hours",
                        ExprKeys.SRC: {
                            ExprKeys.SRC_LINE: lines[2],
                            ExprKeys.SRC_LINE_NUM: 3,
                        },
                        ExprKeys.TYPE: TextTypes.simple.name_expr,
                        ExprKeys.VALUE: "24",
                    },
                    {
                        ExprKeys.FIELD: "agg:installed_software",
                        ExprKeys.IDX: 3,
                        ExprKeys.LOG: "and",
                        ExprKeys.SRC: {
                            ExprKeys.SRC_LINE: lines[3],
                            ExprKeys.SRC_LINE_NUM: 4,
                        },
                        ExprKeys.SUBS: [
                            {
                                ExprKeys.IDX: 4,
                                ExprKeys.OP: "equals",
                                ExprKeys.SRC: {
                                    ExprKeys.SRC_LINE: lines[4],
                                    ExprKeys.SRC_LINE_NUM: 5,
                                },
                                ExprKeys.SUB: "name",
                                ExprKeys.VALUE: "Google Chrome",
                            },
                            {
                                ExprKeys.IDX: 5,
                                ExprKeys.OP: "less_than",
                                ExprKeys.SRC: {
                                    ExprKeys.SRC_LINE: lines[5],
                                    ExprKeys.SRC_LINE_NUM: 6,
                                },
                                ExprKeys.SUB: "version",
                                ExprKeys.VALUE: "99",
                            },
                        ],
                        ExprKeys.TYPE: TextTypes.start_complex.name_expr,
                    },
                ],
                ExprKeys.TYPE: TextTypes.start_bracket.name_expr,
            },
            {
                ExprKeys.FIELD: "last_seen",
                ExprKeys.IDX: 8,
                ExprKeys.OP: "last_hours",
                ExprKeys.SRC: {ExprKeys.SRC_LINE: lines[8], ExprKeys.SRC_LINE_NUM: 9},
                ExprKeys.TYPE: TextTypes.simple.name_expr,
                ExprKeys.VALUE: "24",
            },
        ]

        content = "\n".join(lines)
        text_wizard = WizardText()
        exprs = text_wizard.from_text(content=content)

        assert exprs == exp

    def test_from_text_simple(self):
        content = f"""
{ExprKeys.FIELD}=last_seen, {ExprKeys.OP}=last_hours, {ExprKeys.VALUE}=24
"""
        lines = content.splitlines()
        exp = [
            {
                ExprKeys.FIELD: "last_seen",
                ExprKeys.IDX: 1,
                ExprKeys.OP: "last_hours",
                ExprKeys.SRC: {ExprKeys.SRC_LINE: lines[1], ExprKeys.SRC_LINE_NUM: 2},
                ExprKeys.TYPE: TextTypes.simple.name_expr,
                ExprKeys.VALUE: "24",
            }
        ]

        content = "\n".join(lines)
        text_wizard = WizardText()
        exprs = text_wizard.from_text(content=content)

        assert exprs == exp

    def test_from_text_complex(self):
        content = f"""
{ExprKeys.TYPE} = {TextTypes.start_complex.name_text.upper()}, {ExprKeys.LOG} = and, {ExprKeys.FIELD}=agg:installed_software
    {ExprKeys.SUB}=name, {ExprKeys.OP}=equals, {ExprKeys.VALUE}="Google Chrome"
    {ExprKeys.SUB}=version, {ExprKeys.OP}=less_than, {ExprKeys.VALUE}=99
{ExprKeys.TYPE}={TextTypes.stop_complex.name_text}
"""  # noqa
        lines = content.splitlines()
        exp = [
            {
                ExprKeys.FIELD: "agg:installed_software",
                ExprKeys.IDX: 1,
                ExprKeys.LOG: "and",
                ExprKeys.SRC: {ExprKeys.SRC_LINE: lines[1], ExprKeys.SRC_LINE_NUM: 2},
                ExprKeys.SUBS: [
                    {
                        ExprKeys.SUB: "name",
                        ExprKeys.IDX: 2,
                        ExprKeys.OP: "equals",
                        ExprKeys.SRC: {
                            ExprKeys.SRC_LINE: lines[2],
                            ExprKeys.SRC_LINE_NUM: 3,
                        },
                        ExprKeys.VALUE: "Google Chrome",
                    },
                    {
                        ExprKeys.SUB: "version",
                        ExprKeys.IDX: 3,
                        ExprKeys.OP: "less_than",
                        ExprKeys.SRC: {
                            ExprKeys.SRC_LINE: lines[3],
                            ExprKeys.SRC_LINE_NUM: 4,
                        },
                        ExprKeys.VALUE: "99",
                    },
                ],
                ExprKeys.TYPE: TextTypes.start_complex.name_expr,
            }
        ]

        text_wizard = WizardText()
        exprs = text_wizard.from_text(content=content)
        assert exprs == exp

    def test_from_text_empty(self):
        content = ""
        text_wizard = WizardText()
        with pytest.raises(ToolsError) as excinfo:
            text_wizard.from_text(content=content)
        assert str(excinfo.value).startswith("Required value ")

    def test_from_text_badtype(self):
        content = 1
        text_wizard = WizardText()
        with pytest.raises(ToolsError) as excinfo:
            text_wizard.from_text(content=content)
        assert str(excinfo.value).startswith("Required type ")

    def test_from_text_no_exprs(self):
        content = """
        # x
        """
        text_wizard = WizardText()
        with pytest.raises(WizardError) as excinfo:
            text_wizard.from_text(content=content)
        assert str(excinfo.value).startswith("No expressions parsed from")

    def test_parse_line_missing_sep_line(self):
        line = "v"
        text_wizard = WizardText()
        with pytest.raises(WizardError) as excinfo:
            text_wizard._parse_line(line=line)
        assert str(excinfo.value).startswith("Missing separator")

    @pytest.mark.parametrize(
        "line",
        [
            "",
            "  ",
            "#",
            "  #",
            "key=",
            "key = ",
            "key =",
            "=value",
            "= value",
            " = value",
        ],
    )
    def test_parse_line_empty_expr(self, line):
        text_wizard = WizardText()
        expr = text_wizard._parse_line(line=line)
        assert isinstance(expr, dict)
        assert not expr

    @pytest.mark.parametrize(
        "line,exp",
        [
            (f"{ExprKeys.FIELD}=hostname", {f"{ExprKeys.FIELD}": "hostname"}),
            (
                f"{ExprKeys.FIELD}=hostname, key2=value2",
                {f"{ExprKeys.FIELD}": "hostname", "key2": "value2"},
            ),
            (
                f"{ExprKeys.FIELD}=hostname, key2 = value2",
                {f"{ExprKeys.FIELD}": "hostname", "key2": "value2"},
            ),
            (
                f'{ExprKeys.FIELD}=hostname, key2 = value2, key3 = " abc def"',
                {ExprKeys.FIELD: "hostname", "key2": "value2", "key3": "abc def"},
            ),
        ],
    )
    def test_parse_line_exp(self, line, exp):
        text_wizard = WizardText()
        expr = text_wizard._parse_line(line=line)
        assert isinstance(expr, dict)
        assert expr == exp

    def test_handle_simple_missing_field(self):
        text_wizard = WizardText()
        with pytest.raises(WizardError) as excinfo:
            text_wizard._handle_simple({})
        assert str(excinfo.value).startswith(f"Missing required key {ExprKeys.FIELD!r}")

    def test_handle_simple_missing_sub(self):
        text_wizard = WizardText()
        text_wizard._expr_complex = {ExprKeys.IDX: 23}
        with pytest.raises(WizardError) as excinfo:
            text_wizard._handle_simple({})
        assert str(excinfo.value).startswith(f"Missing required key {ExprKeys.SUB!r}")

    def test_expr_bad_type(self):
        stype = "badwolf"
        expr = {ExprKeys.TYPE: stype}
        text_wizard = WizardText()
        with pytest.raises(WizardError) as excinfo:
            text_wizard._parse_expr(expr=expr)
        assert str(excinfo.value).startswith(f"Invalid type {stype!r}, valids:")

    def test_stop_bracket_ok(self):
        text_wizard = WizardText()
        text_wizard._expr_bracket = {ExprKeys.IDX: 23}
        text_wizard._handle_stop_bracket(expr={})
        assert not text_wizard._expr_bracket

    def test_stop_bracket_bad(self):
        text_wizard = WizardText()
        text_wizard._expr_bracket = None
        with pytest.raises(WizardError) as excinfo:
            text_wizard._handle_stop_bracket(expr={})
        assert str(excinfo.value).startswith(
            f"Can not stop a {TextTypes.start_bracket.name_expr}"
        )

    def test_stop_complex_ok(self):
        text_wizard = WizardText()
        text_wizard._expr_complex = {ExprKeys.IDX: 23}
        text_wizard._handle_stop_complex(expr={})
        assert not text_wizard._expr_complex

    def test_stop_complex_bad(self):
        text_wizard = WizardText()
        text_wizard._expr_complex = None
        with pytest.raises(WizardError) as excinfo:
            text_wizard._handle_stop_complex(expr={})
        assert str(excinfo.value).startswith(
            f"Can not stop a {TextTypes.start_complex.name_expr}"
        )

    def test_start_bracket_ok(self):
        text_wizard = WizardText()
        expr = {ExprKeys.TYPE: TextTypes.start_bracket.name_text}
        exp = {
            **expr,
            ExprKeys.TYPE: TextTypes.start_bracket.name_expr,
            ExprKeys.SUBS: [],
        }
        text_wizard._handle_start_bracket(expr=expr)
        assert text_wizard._expr_bracket == exp

    def test_start_bracket_bad1(self):
        text_wizard = WizardText()
        text_wizard._expr_bracket = {ExprKeys.IDX: 23}
        expr = {ExprKeys.TYPE: TextTypes.start_bracket.name_text}
        with pytest.raises(WizardError) as excinfo:
            text_wizard._handle_start_bracket(expr=expr)
        assert str(excinfo.value).startswith(
            f"Can not start a {TextTypes.start_bracket.name_expr}"
        )

    def test_start_bracket_bad2(self):
        text_wizard = WizardText()
        text_wizard._expr_complex = {ExprKeys.IDX: 23}
        expr = {ExprKeys.TYPE: TextTypes.start_bracket.name_text}
        with pytest.raises(WizardError) as excinfo:
            text_wizard._handle_start_bracket(expr=expr)
        assert str(excinfo.value).startswith(
            f"Can not start a {TextTypes.start_bracket.name_expr}"
        )

    def test_start_complex_ok(self):
        text_wizard = WizardText()
        expr = {
            ExprKeys.TYPE: TextTypes.start_complex.name_text,
            ExprKeys.FIELD: "hostname",
        }
        exp = {
            **expr,
            ExprKeys.TYPE: TextTypes.start_complex.name_expr,
            ExprKeys.SUBS: [],
        }
        text_wizard._handle_start_complex(expr=expr)
        assert text_wizard._expr_complex == exp

    def test_start_complex_bad(self):
        text_wizard = WizardText()
        text_wizard._expr_complex = {ExprKeys.IDX: 23, ExprKeys.FIELD: "hostname"}
        expr = {ExprKeys.TYPE: TextTypes.start_complex.name_text}
        with pytest.raises(WizardError) as excinfo:
            text_wizard._handle_start_complex(expr=expr)
        assert str(excinfo.value).startswith(
            f"Can not start a {TextTypes.start_complex.name_expr}"
        )
