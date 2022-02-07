# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.query_wizard."""
import pytest

from axonius_api_client.api.wizards import WizardCsv
from axonius_api_client.constants.wizards import Entry, EntrySq, Results, Types
from axonius_api_client.exceptions import WizardError
from axonius_api_client.parsers.wizards import WizardParser

from ...utils import get_schema
from .test_wizard import TestData

SRC = "test moo"


class TestWizardCsv:
    @pytest.fixture(params=["api_devices", "api_users"])
    def wizard(self, request):
        apiobj = request.getfixturevalue(request.param)
        obj = WizardCsv(apiobj=apiobj)
        assert obj.APIOBJ == apiobj
        assert isinstance(obj.PARSER, WizardParser)
        return obj


class TestRowsToEntry(TestWizardCsv):
    def test_valid(self, wizard):
        rows = [
            {Entry.TYPE: "", Entry.VALUE: "xx"},
            {Entry.TYPE: Types.SAVED_QUERY, Entry.VALUE: "xx"},
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: "xx"},
            {Entry.TYPE: "# ", Entry.VALUE: "xx"},
        ]
        exp = [
            {
                Entry.TYPE: Types.SAVED_QUERY,
                Entry.VALUE: "xx",
                Entry.SRC: (
                    f"{SRC} row #2:\n  {Entry.TYPE}: {Types.SAVED_QUERY}\n  {Entry.VALUE}: xx"
                ),
                **EntrySq.OPT,
            },
            {
                Entry.TYPE: Types.SIMPLE,
                Entry.VALUE: "xx",
                Entry.SRC: f"{SRC} row #3:\n  {Entry.TYPE}: {Types.SIMPLE}\n  {Entry.VALUE}: xx",
            },
        ]
        ret = wizard._rows_to_entries(rows=rows, source=SRC)
        assert ret == exp

    def test_invalid_type(self, wizard):
        rows = [
            {Entry.TYPE: "badwolf", Entry.VALUE: "xx"},
        ]
        with pytest.raises(WizardError) as exc:
            wizard._rows_to_entries(rows=rows, source=SRC)
        assert "Error parsing row to entry" in str(exc.value)
        assert "Invalid type" in str(exc.value)

    def test_empty_value(self, wizard):
        rows = [
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: "  "},
        ]
        with pytest.raises(WizardError) as exc:
            wizard._rows_to_entries(rows=rows, source=SRC)
        assert "Error parsing row to entry" in str(exc.value)
        assert "Empty value for column" in str(exc.value)


class TestRowToEntry(TestWizardCsv):
    @pytest.mark.parametrize(
        "row, exp",
        [
            [
                {Entry.TYPE: Types.SIMPLE, Entry.VALUE: "xx", "EXTRA": "b"},
                {Entry.TYPE: Types.SIMPLE, Entry.VALUE: "xx"},
            ],
            [
                {Entry.TYPE: Types.COMPLEX, Entry.VALUE: "xx", "EXTRA": "b"},
                {Entry.TYPE: Types.COMPLEX, Entry.VALUE: "xx"},
            ],
            [
                {Entry.TYPE: Types.SAVED_QUERY, Entry.VALUE: "xx", "EXTRA": "b"},
                {Entry.TYPE: Types.SAVED_QUERY, Entry.VALUE: "xx"},
            ],
            [
                {Entry.TYPE: "", Entry.VALUE: "xx"},
                {},
            ],
            [
                {Entry.TYPE: "# abc", Entry.VALUE: "xx"},
                {},
            ],
        ],
    )
    def test_valid(self, wizard, row, exp):
        if row[Entry.TYPE] == Types.SAVED_QUERY:
            exp.update(EntrySq.OPT)
        if exp:
            exp[Entry.SRC] = SRC
        ret = wizard._row_to_entry(row=row, src=SRC)
        assert ret == exp

    @pytest.mark.parametrize(
        "row",
        [
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: ""},
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: None},
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: 2},
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: True},
        ],
    )
    def test_invalid(self, wizard, row):
        with pytest.raises(WizardError) as exc:
            wizard._row_to_entry(row=row, src=SRC)

        assert "Empty value for column" in str(exc.value)


class TestProcessDesc(TestWizardCsv):
    @pytest.mark.parametrize(
        "entry, exp",
        [
            [{}, None],
            [{EntrySq.DESC: ""}, None],
            [{EntrySq.DESC: None}, None],
            [{EntrySq.DESC: 2}, "2"],
            [{EntrySq.DESC: "boom"}, "boom"],
        ],
    )
    def test_valid(self, wizard, entry, exp):
        ret = wizard._process_desc(entry=entry)
        assert ret == exp


class TestProcessTags(TestWizardCsv):
    @pytest.mark.parametrize(
        "entry, exp",
        [
            [{}, None],
            [{EntrySq.TAGS: ""}, None],
            [{EntrySq.TAGS: None}, None],
            [{EntrySq.TAGS: 2}, ["2"]],
            [{EntrySq.TAGS: "boom,foo,boo"}, ["boom", "foo", "boo"]],
        ],
    )
    def test_valid(self, wizard, entry, exp):
        ret = wizard._process_tags(entry=entry)
        assert ret == exp


class TestProcessFields(TestWizardCsv):
    @pytest.mark.parametrize(
        "entry",
        [
            {},
            {EntrySq.FIELDS: ""},
            {EntrySq.FIELDS: None},
        ],
    )
    def test_default(self, wizard, entry):
        exp = wizard.APIOBJ.fields_default
        ret = wizard._process_fields(entry=entry)
        assert ret == exp

    def test_no_default(self, wizard):
        simple = wizard.APIOBJ.FIELD_SIMPLE
        cplex = wizard.APIOBJ.FIELD_COMPLEX
        get_schema(apiobj=wizard.APIOBJ, field=cplex)

        entry = {EntrySq.FIELDS: f"{simple},{cplex}"}
        exp = [simple, cplex]
        ret = wizard._process_fields(entry=entry)
        assert ret == exp

    def test_with_default(self, wizard):
        cplex = wizard.APIOBJ.FIELD_COMPLEX
        get_schema(apiobj=wizard.APIOBJ, field=cplex)
        cplex_sub = f"{cplex}.{wizard.APIOBJ.FIELD_COMPLEX_SUB}"
        entry = {EntrySq.FIELDS: f"{cplex},{EntrySq.DEFAULT},{cplex_sub}"}
        exp = [cplex, *wizard.APIOBJ.fields_default, cplex_sub]
        ret = wizard._process_fields(entry=entry)
        assert ret == exp


class TestProcessSqNewSq(TestWizardCsv, TestData):
    def test_no_entries(self, wizard):
        entry = {Entry.VALUE: "badwolf", EntrySq.TAGS: "tag1,tag2", EntrySq.DESC: SRC}
        exp = {
            EntrySq.NAME: "badwolf",
            EntrySq.FDEF: False,
            EntrySq.FMAN: wizard.APIOBJ.fields_default,
            EntrySq.TAGS: ["tag1", "tag2"],
            EntrySq.DESC: SRC,
            **EntrySq.OPT_ENTRY,
        }
        wizard._new_sq(entry=entry)
        assert wizard.SQ == exp
        assert exp in wizard.SQS
        assert wizard.SQ_ENTRIES == []

        wizard._process_sq_entries()
        assert exp in wizard.SQS_DONE

    def test_with_entries(self, wizard, test_data1):
        entry = {Entry.VALUE: "badwolf", EntrySq.TAGS: "tag1,tag2", EntrySq.DESC: SRC}
        exp = {
            EntrySq.NAME: "badwolf",
            EntrySq.FDEF: False,
            EntrySq.FMAN: wizard.APIOBJ.fields_default,
            EntrySq.TAGS: ["tag1", "tag2"],
            EntrySq.DESC: SRC,
            **EntrySq.OPT_ENTRY,
        }
        wizard._new_sq(entry=entry)
        assert wizard.SQ == exp
        assert exp in wizard.SQS
        assert wizard.SQ_ENTRIES == []

        entries, exp_exprs, exp_query = test_data1
        wizard.SQ_ENTRIES = entries
        wizard._process_sq_entries()
        exp[Results.EXPRS] = exp_exprs
        exp[Results.QUERY] = exp_query

        assert exp == wizard.SQ
        assert exp in wizard.SQS_DONE


class TestProcessSq(TestWizardCsv):
    def test_sq_not_first(self, wizard):
        entry = {Entry.TYPE: Types.SIMPLE, Entry.VALUE: "xx", Entry.SRC: SRC}
        with pytest.raises(WizardError) as exc:
            wizard._process_sq(entry=entry, is_last=False)
        assert "First row must be type" in str(exc.value)

    def test_sq_no_entries(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SAVED_QUERY,
            Entry.VALUE: "badwolf",
            EntrySq.TAGS: "tag1,tag2",
            EntrySq.DESC: SRC,
            Entry.SRC: SRC,
        }
        exp_sq = {
            EntrySq.NAME: "badwolf",
            EntrySq.FDEF: False,
            EntrySq.FMAN: wizard.APIOBJ.fields_default,
            EntrySq.TAGS: ["tag1", "tag2"],
            EntrySq.DESC: SRC,
            **EntrySq.OPT_ENTRY,
        }
        exp1_ret = 1
        exp1_entries = []
        ret1 = wizard._process_sq(entry=entry1, is_last=False)
        assert ret1 == exp1_ret
        assert wizard.SQ == exp_sq
        assert wizard.SQ_ENTRIES == exp1_entries

    def test_sq_entries_is_last_true(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SAVED_QUERY,
            Entry.VALUE: "badwolf",
            EntrySq.TAGS: "tag1,tag2",
            EntrySq.DESC: SRC,
            Entry.SRC: SRC,
        }
        exp1_sq = {
            EntrySq.NAME: "badwolf",
            EntrySq.FDEF: False,
            EntrySq.FMAN: wizard.APIOBJ.fields_default,
            EntrySq.TAGS: ["tag1", "tag2"],
            EntrySq.DESC: SRC,
            **EntrySq.OPT_ENTRY,
        }
        exp1_entries = []
        exp1_ret = 1
        ret1 = wizard._process_sq(entry=entry1, is_last=False)
        assert ret1 == exp1_ret
        assert wizard.SQ == exp1_sq
        assert wizard.SQ_ENTRIES == exp1_entries

        simple = wizard.APIOBJ.FIELD_SIMPLE

        entry2 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{simple} equals boom",
            Entry.SRC: SRC,
        }
        exp2_sq = exp1_sq
        exp2_sq[Results.EXPRS] = [
            {
                "bracketWeight": 0,
                "children": [
                    {
                        "condition": "",
                        "expression": {
                            "compOp": "",
                            "field": "",
                            "filteredAdapters": None,
                            "value": None,
                        },
                        "i": 0,
                    }
                ],
                "compOp": "equals",
                "field": f"{simple}",
                "fieldType": "axonius",
                "filter": f'("{simple}" == "boom")',
                "filteredAdapters": None,
                "leftBracket": False,
                "logicOp": "",
                "not": False,
                "rightBracket": False,
                "value": "boom",
            }
        ]
        exp2_sq[Results.QUERY] = f'("{simple}" == "boom")'

        exp2_entries = [
            {
                Entry.TYPE: Types.SIMPLE,
                Entry.VALUE: f"{simple} equals boom",
                Entry.SRC: SRC,
                Entry.FLAGS: [],
                Entry.WEIGHT: 0,
            }
        ]
        exp2_ret = 2
        ret2 = wizard._process_sq(entry=entry2, is_last=True)
        assert ret2 == exp2_ret
        assert wizard.SQ == exp2_sq
        assert wizard.SQ_ENTRIES == exp2_entries

    def test_sq_entries_sq(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SAVED_QUERY,
            Entry.VALUE: "badwolf",
            EntrySq.TAGS: "tag1,tag2",
            EntrySq.DESC: SRC,
            Entry.SRC: SRC,
        }
        exp1_sq = {
            EntrySq.NAME: "badwolf",
            EntrySq.FDEF: False,
            EntrySq.FMAN: wizard.APIOBJ.fields_default,
            EntrySq.TAGS: ["tag1", "tag2"],
            EntrySq.DESC: SRC,
            **EntrySq.OPT_ENTRY,
        }
        exp1_entries = []
        exp1_ret = 1
        ret1 = wizard._process_sq(entry=entry1, is_last=False)
        assert ret1 == exp1_ret
        assert wizard.SQ == exp1_sq
        assert wizard.SQ_ENTRIES == exp1_entries

        simple = wizard.APIOBJ.FIELD_SIMPLE

        entry2 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{simple} equals boom",
            Entry.SRC: SRC,
        }
        exp2_sq = exp1_sq
        exp2_entries = [
            {
                Entry.TYPE: Types.SIMPLE,
                Entry.VALUE: f"{simple} equals boom",
                Entry.SRC: SRC,
            }
        ]
        exp2_ret = 3
        ret2 = wizard._process_sq(entry=entry2, is_last=False)
        assert ret2 == exp2_ret
        assert wizard.SQ == exp2_sq
        assert wizard.SQ_ENTRIES == exp2_entries

        entry3 = {
            Entry.TYPE: Types.SAVED_QUERY,
            Entry.VALUE: "badwolf3",
            EntrySq.TAGS: "tag1,tag2",
            EntrySq.DESC: SRC,
            Entry.SRC: SRC,
        }
        exp3_sq = {
            EntrySq.NAME: "badwolf3",
            EntrySq.FDEF: False,
            EntrySq.FMAN: wizard.APIOBJ.fields_default,
            EntrySq.TAGS: ["tag1", "tag2"],
            EntrySq.DESC: SRC,
            **EntrySq.OPT_ENTRY,
        }
        exp3_entries = []
        exp3_ret = 0
        ret3 = wizard._process_sq(entry=entry3, is_last=False)
        assert ret3 == exp3_ret
        assert wizard.SQ == exp3_sq
        assert wizard.SQ_ENTRIES == exp3_entries


class TestProcessSqs(TestWizardCsv):
    def test_sq_not_first(self, wizard):
        entries = [{Entry.TYPE: Types.SIMPLE, Entry.VALUE: "xx", Entry.SRC: SRC}]
        with pytest.raises(WizardError) as exc:
            wizard._process_sqs(entries=entries)
        assert "First row must be type" in str(exc.value)
        assert "Error parsing entry from" in str(exc.value)

    def test_full_barrel(self, wizard):
        simple = wizard.APIOBJ.FIELD_SIMPLE
        entries = [
            {
                Entry.TYPE: Types.SAVED_QUERY,
                Entry.VALUE: "badwolf",
                EntrySq.TAGS: "tag1,tag2",
                EntrySq.DESC: SRC,
                Entry.SRC: SRC,
            },
            {
                Entry.TYPE: Types.SIMPLE,
                Entry.VALUE: f"{simple} equals boom",
                Entry.SRC: SRC,
            },
            {
                Entry.TYPE: Types.SAVED_QUERY,
                Entry.VALUE: "badwolf3",
                EntrySq.TAGS: "tag1,tag2",
                EntrySq.DESC: SRC,
                Entry.SRC: SRC,
            },
        ]
        exp = [
            {
                EntrySq.NAME: "badwolf",
                EntrySq.FDEF: False,
                EntrySq.FMAN: wizard.APIOBJ.fields_default,
                EntrySq.TAGS: ["tag1", "tag2"],
                EntrySq.DESC: SRC,
                Results.EXPRS: [
                    {
                        "bracketWeight": 0,
                        "children": [
                            {
                                "condition": "",
                                "expression": {
                                    "compOp": "",
                                    "field": "",
                                    "filteredAdapters": None,
                                    "value": None,
                                },
                                "i": 0,
                            }
                        ],
                        "compOp": "equals",
                        "field": f"{simple}",
                        "fieldType": "axonius",
                        "filter": f'("{simple}" == "boom")',
                        "filteredAdapters": None,
                        "leftBracket": False,
                        "logicOp": "",
                        "not": False,
                        "rightBracket": False,
                        "value": "boom",
                    }
                ],
                Results.QUERY: f'("{simple}" == "boom")',
                **EntrySq.OPT_ENTRY,
            },
            {
                EntrySq.NAME: "badwolf3",
                EntrySq.FDEF: False,
                EntrySq.FMAN: wizard.APIOBJ.fields_default,
                EntrySq.TAGS: ["tag1", "tag2"],
                EntrySq.DESC: SRC,
                **EntrySq.OPT_ENTRY,
            },
        ]
        ret = wizard._process_sqs(entries=entries)
        assert ret == exp


class TestProcessCsv(TestWizardCsv):
    def test_missing_columns(self, wizard):
        columns = ["x", "b"]
        rows = [{"a": "b"}]
        with pytest.raises(WizardError) as exc:
            wizard._process_csv(columns=columns, rows=rows, source=SRC)
        assert "Missing required columns" in str(exc.value)

    def test_empty_rows(self, wizard):
        columns = EntrySq.REQ
        rows = []
        with pytest.raises(WizardError) as exc:
            wizard._process_csv(columns=columns, rows=rows, source=SRC)
        assert "No rows found" in str(exc.value)

    def test_empty_rows_post_parse(self, wizard):
        columns = EntrySq.REQ
        rows = [{Entry.TYPE: ""}, {Entry.TYPE: " # moo"}]
        with pytest.raises(WizardError) as exc:
            wizard._process_csv(columns=columns, rows=rows, source=SRC)
        assert "No rows found" in str(exc.value)

    def test_valid(self, wizard):
        columns = EntrySq.REQ
        rows = [
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: "xx"},
            {Entry.TYPE: Types.COMPLEX, Entry.VALUE: "xx"},
            {Entry.TYPE: Types.SAVED_QUERY, Entry.VALUE: "xx"},
        ]
        exp = [
            {
                Entry.TYPE: Types.SIMPLE,
                Entry.VALUE: "xx",
                Entry.SRC: f"{SRC} row #1:\n  {Entry.TYPE}: {Types.SIMPLE}\n  value: xx",
            },
            {
                Entry.TYPE: Types.COMPLEX,
                Entry.VALUE: "xx",
                Entry.SRC: f"{SRC} row #2:\n  {Entry.TYPE}: {Types.COMPLEX}\n  value: xx",
            },
            {
                Entry.TYPE: Types.SAVED_QUERY,
                Entry.VALUE: "xx",
                Entry.SRC: f"{SRC} row #3:\n  {Entry.TYPE}: {Types.SAVED_QUERY}\n  value: xx",
                **EntrySq.OPT,
            },
        ]
        ret = wizard._process_csv(columns=columns, rows=rows, source=SRC)
        assert ret == exp


class TestLoadCsv(TestWizardCsv):
    def test_valid(self, wizard):
        simple = wizard.APIOBJ.FIELD_SIMPLE
        content = f"""
{Entry.TYPE},{Entry.VALUE},{EntrySq.DESC},{EntrySq.TAGS},{EntrySq.FIELDS}
"{Types.SAVED_QUERY}","badwolf","it is bad","tag1,tag2",""
"{Types.SIMPLE}","{simple} contains boom",,,
"""
        exp = [
            {
                Entry.TYPE: Types.SAVED_QUERY,
                Entry.VALUE: "badwolf",
                Entry.SRC: (
                    f"{SRC} row #1:\n  {Entry.TYPE}: {Types.SAVED_QUERY}\n  "
                    f"{Entry.VALUE}: badwolf\n  {EntrySq.DESC}: it is bad\n  "
                    f"{EntrySq.TAGS}: tag1,tag2\n  {EntrySq.FIELDS}: "
                ),
                EntrySq.DESC: "it is bad",
                EntrySq.TAGS: "tag1,tag2",
                EntrySq.FIELDS: EntrySq.OPT[EntrySq.FIELDS],
                **EntrySq.OPT_ENTRY,
            },
            {
                Entry.TYPE: Types.SIMPLE,
                Entry.VALUE: f"{simple} contains boom",
                Entry.SRC: (
                    f"{SRC} row #2:\n  {Entry.TYPE}: {Types.SIMPLE}\n  {Entry.VALUE}: {simple} "
                    f"contains boom\n  {EntrySq.DESC}: \n  {EntrySq.TAGS}: \n  {EntrySq.FIELDS}: "
                ),
            },
        ]
        ret = wizard._load_csv(content=content, source=SRC)
        assert exp == ret


class TestParse(TestWizardCsv):
    def test_valid(self, wizard, tmp_path):
        simple = wizard.APIOBJ.FIELD_SIMPLE
        content = f"""
{Entry.TYPE},{Entry.VALUE},{EntrySq.DESC},{EntrySq.TAGS},{EntrySq.FIELDS}
"{Types.SAVED_QUERY}","badwolf","it is bad","tag1,tag2",""
"{Types.SIMPLE}","{simple} contains boom",,,
"""
        path = tmp_path / "test.csv"
        path.write_text(content)

        exp = [
            {
                EntrySq.NAME: "badwolf",
                EntrySq.FDEF: False,
                EntrySq.FMAN: wizard.APIOBJ.fields_default,
                EntrySq.TAGS: ["tag1", "tag2"],
                EntrySq.DESC: "it is bad",
                Results.EXPRS: [
                    {
                        "bracketWeight": 0,
                        "children": [
                            {
                                "condition": "",
                                "expression": {
                                    "compOp": "",
                                    "field": "",
                                    "filteredAdapters": None,
                                    "value": None,
                                },
                                "i": 0,
                            }
                        ],
                        "compOp": "contains",
                        "field": f"{simple}",
                        "fieldType": "axonius",
                        "filter": f'("{simple}" == regex("boom", "i"))',
                        "filteredAdapters": None,
                        "leftBracket": False,
                        "logicOp": "",
                        "not": False,
                        "rightBracket": False,
                        "value": "boom",
                    }
                ],
                Results.QUERY: f'("{simple}" == regex("boom", "i"))',
                **EntrySq.OPT_ENTRY,
            }
        ]
        ret_str = wizard.parse(content=content, source=SRC)
        assert exp == ret_str

        ret_path = wizard.parse_path(path=path, source=SRC)
        assert exp == ret_path
