# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.wizard.wizard"""
import pytest

from axonius_api_client.api.wizards import Wizard
from axonius_api_client.constants.fields import ALL_NAME, Operators
from axonius_api_client.constants.wizards import Entry, Flags, Results, Types
from axonius_api_client.exceptions import NotFoundError, WizardError
from axonius_api_client.parsers.wizards import WizardParser

from ...utils import get_schema


class TestWizard:
    @pytest.fixture(params=["api_devices", "api_users"])
    def wizard(self, request):
        apiobj = request.getfixturevalue(request.param)
        obj = Wizard(apiobj=apiobj)
        assert obj.APIOBJ == apiobj
        assert isinstance(obj.PARSER, WizardParser)
        return obj


class TestData:
    @pytest.fixture
    def test_data1(self, wizard):
        simple = wizard.APIOBJ.FIELD_SIMPLE
        cplex = wizard.APIOBJ.FIELD_COMPLEX
        sub = wizard.APIOBJ.FIELD_COMPLEX_SUB
        get_schema(apiobj=wizard.APIOBJ, field=cplex)

        entries = [
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: f"{simple} exists"},
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: f"{simple} contains test"},
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: f"|{simple} contains dev"},
            {Entry.TYPE: Types.SIMPLE, Entry.VALUE: f"{cplex} exists"},
            {
                Entry.TYPE: Types.COMPLEX,
                Entry.VALUE: f"!{cplex} // {sub} contains boom",
            },
        ]
        exp_exprs = [
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
                "compOp": "exists",
                "field": f"{simple}",
                "fieldType": "axonius",
                "filter": f'(("{simple}" == ({{"$exists":true,"$ne":""}})))',
                "filteredAdapters": None,
                "leftBracket": False,
                "logicOp": "",
                "not": False,
                "rightBracket": False,
                "value": None,
            },
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
                "filter": f'and ("{simple}" == regex("test", "i"))',
                "filteredAdapters": None,
                "i": 1,
                "leftBracket": False,
                "logicOp": "and",
                "not": False,
                "rightBracket": False,
                "value": "test",
            },
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
                "filter": f'or ("{simple}" == regex("dev", "i"))',
                "filteredAdapters": None,
                "i": 2,
                "leftBracket": False,
                "logicOp": "or",
                "not": False,
                "rightBracket": False,
                "value": "dev",
            },
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
                "compOp": "exists",
                "field": f"{cplex}",
                "fieldType": "axonius",
                "filter": (
                    f'and (("{cplex}" == ({{"$exists":true,"$ne":[]}})) and "{cplex}" != [])'
                ),
                "filteredAdapters": None,
                "i": 3,
                "leftBracket": False,
                "logicOp": "and",
                "not": False,
                "rightBracket": False,
                "value": None,
            },
            {
                "bracketWeight": 0,
                "children": [
                    {
                        "condition": f'("{sub}" == regex("boom", "i"))',
                        "expression": {
                            "compOp": "contains",
                            "field": f"{sub}",
                            "filteredAdapters": None,
                            "value": "boom",
                        },
                        "i": 0,
                    }
                ],
                "compOp": "",
                "field": f"{cplex}",
                "fieldType": "axonius",
                "filter": (f'and not ("{cplex}" == match([("{sub}" == regex("boom", "i"))]))'),
                "filteredAdapters": None,
                "i": 4,
                "leftBracket": False,
                "logicOp": "and",
                "not": True,
                "rightBracket": False,
                "value": None,
                "context": "OBJ",
            },
        ]
        exp_query = (
            f'(("{simple}" == ({{"$exists":true,"$ne":""}}))) and ("{simple}" == '
            f'regex("test", "i")) or ("{simple}" == regex("dev", "i")) and (("{cplex}" '
            f'== ({{"$exists":true,"$ne":[]}})) and "{cplex}" != []) and not ("{cplex}" '
            f'== match([("{sub}" == regex("boom", "i"))]))'
        )
        return entries, exp_exprs, exp_query


class TestCheckEntryType(TestWizard):
    def test_invalid(self, wizard):
        with pytest.raises(WizardError) as exc:
            wizard._check_entry_type(etype="badwolf", types=Types.DICT)
        assert "Invalid type" in str(exc.value)

    def test_valid(self, wizard):
        ret = wizard._check_entry_type(etype=Types.DICT[0].upper(), types=Types.DICT)
        assert ret == Types.DICT[0]


class TestGetField(TestWizard):
    @pytest.mark.parametrize(
        "field, value_raw, exc_str",
        [
            [ALL_NAME, f"{ALL_NAME} blah blah", "Can not use"],
            ["badwolf", "badwolf blah blah", "Unable to find FIELD"],
        ],
    )
    def test_invalid(self, wizard, field, value_raw, exc_str):
        with pytest.raises(WizardError) as exc:
            wizard._get_field(value=field, value_raw=value_raw)
        assert exc_str in str(exc)

    def test_valid(self, wizard):
        field = wizard.APIOBJ.FIELD_SIMPLE
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
        field = wizard.APIOBJ.FIELD_COMPLEX
        get_schema(apiobj=wizard.APIOBJ, field=field)
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

    @pytest.mark.parametrize(
        "entry, keys",
        [
            [{Entry.TYPE: "xxx", Entry.VALUE: "y"}, Entry.REQ],
        ],
    )
    def test_valid(self, wizard, entry, keys):
        wizard._check_entry_keys(entry=entry, keys=keys)


class TestSplitFlags(TestWizard):
    @pytest.mark.parametrize(
        "value_raw, exp",
        [
            [
                f"{Flags.NOT} @ $ hostname contains blah  {Flags.RIGHTB}",
                ([Flags.NOT, "@", "$", Flags.RIGHTB], "hostname contains blah "),
            ],
            [
                f" {Flags.NOT} {Flags.AND} hostname contains blah {Flags.RIGHTB}",
                ([Flags.NOT, Flags.AND, Flags.RIGHTB], "hostname contains blah"),
            ],
            [
                f"{Flags.NOT}{Flags.OR}hostname contains blah{Flags.RIGHTB}",
                ([Flags.NOT, Flags.OR, Flags.RIGHTB], "hostname contains blah"),
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
            # ["badwolf 232 blah", "OPERATOR"],
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


class TestParseFlags(TestWizard):
    def test_valid1(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{Flags.NOT} @ $ hostname contains blah  {Flags.RIGHTB}",
        }
        entries = [entry1]
        is_open = False
        tracker = 0

        exp1_entry = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah ",
            Entry.FLAGS: [Flags.NOT, "@", "$", Flags.RIGHTB, Flags.LEFTB],
            Entry.WEIGHT: -1,
        }

        exp1_is_open = False
        exp1_tracker = 0
        ret1_entry, is_open, tracker = wizard._parse_flags(
            entry=entry1, idx=0, entries=entries, tracker=tracker, is_open=is_open
        )
        assert ret1_entry == exp1_entry
        assert is_open == exp1_is_open
        assert tracker == exp1_tracker

    def test_valid2(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{Flags.NOT} @ $ hostname contains blah ",
        }
        entries = [entry1]
        is_open = False
        tracker = 0

        exp_entry = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah ",
            Entry.FLAGS: [Flags.NOT, "@", "$"],
            Entry.WEIGHT: 0,
        }
        exp_is_open = False
        exp_tracker = 0
        ret_entry, is_open, tracker = wizard._parse_flags(
            entry=entry1, idx=0, entries=entries, tracker=tracker, is_open=is_open
        )
        assert ret_entry == exp_entry
        assert is_open == exp_is_open
        assert tracker == exp_tracker

    def test_valid3(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{Flags.NOT}{Flags.LEFTB} hostname contains blah ",
        }
        entry2 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{Flags.NOT}{Flags.LEFTB}hostname contains blah ",
        }
        entries = [entry1, entry2]
        is_open = False
        tracker = 0

        exp1_entry = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah ",
            Entry.FLAGS: [Flags.NOT, Flags.LEFTB],
            Entry.WEIGHT: -1,
        }
        exp1_is_open = True
        exp1_tracker = 0
        ret1_entry, is_open, tracker = wizard._parse_flags(
            entry=entry1, idx=0, entries=entries, tracker=tracker, is_open=is_open
        )
        assert ret1_entry == exp1_entry
        assert is_open == exp1_is_open
        assert tracker == exp1_tracker

        exp2_entry = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah ",
            Entry.FLAGS: [Flags.NOT, Flags.LEFTB, Flags.RIGHTB],
            Entry.WEIGHT: -1,
        }
        exp2_is_open = True
        exp2_tracker = 0
        ret2_entry, ret2_is_open, ret2_tracker = wizard._parse_flags(
            entry=entry2, idx=1, entries=entries, tracker=tracker, is_open=is_open
        )
        assert ret2_entry == exp2_entry
        assert is_open == exp2_is_open
        assert tracker == exp2_tracker

        assert entry1[Entry.FLAGS] == [Flags.NOT, Flags.LEFTB, Flags.RIGHTB]

    def test_valid4(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{Flags.LEFTB}hostname contains blah ",
        }
        entry2 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah ",
        }
        entry3 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"hostname contains blah{Flags.RIGHTB}",
        }
        entry4 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah",
        }

        entries = [entry1, entry2, entry3, entry4]

        is_open = False
        tracker = 0

        exp1_entry = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah ",
            Entry.FLAGS: [Flags.LEFTB],
            Entry.WEIGHT: -1,
        }
        exp1_is_open = True
        exp1_tracker = 0
        ret1_entry, is_open, tracker = wizard._parse_flags(
            entry=entry1, idx=0, entries=entries, tracker=tracker, is_open=is_open
        )
        assert ret1_entry == exp1_entry
        assert is_open == exp1_is_open
        assert tracker == exp1_tracker

        exp2_entry = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah ",
            Entry.FLAGS: [],
            Entry.WEIGHT: 1,
        }

        exp2_is_open = True
        exp2_tracker = 1
        ret2_entry, is_open, tracker = wizard._parse_flags(
            entry=entry2, idx=1, entries=entries, tracker=tracker, is_open=is_open
        )
        assert ret2_entry == exp2_entry
        assert is_open == exp2_is_open
        assert tracker == exp2_tracker

        exp3_entry = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah",
            Entry.FLAGS: [Flags.RIGHTB],
            Entry.WEIGHT: 2,
        }

        exp3_is_open = False
        exp3_tracker = 0
        ret3_entry, is_open, tracker = wizard._parse_flags(
            entry=entry3, idx=2, entries=entries, tracker=tracker, is_open=is_open
        )
        assert ret3_entry == exp3_entry
        assert is_open == exp3_is_open
        assert tracker == exp3_tracker

        exp4_entry = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah",
            Entry.FLAGS: [],
            Entry.WEIGHT: 0,
        }

        exp4_is_open = False
        exp4_tracker = 0
        ret4_entry, is_open, tracker = wizard._parse_flags(
            entry=entry4, idx=3, entries=entries, tracker=tracker, is_open=is_open
        )
        assert ret4_entry == exp4_entry
        assert is_open == exp4_is_open
        assert tracker == exp4_tracker


class TestParseEntries(TestWizard):
    def test_valid(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{Flags.LEFTB}hostname contains blah ",
        }
        entry2 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah ",
        }
        entry3 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"hostname contains blah{Flags.RIGHTB}",
        }
        entry4 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: "hostname contains blah",
        }

        entries = [entry1, entry2, entry3, entry4]
        source = "a test..."
        exp = [
            {
                Entry.TYPE: "simple",
                Entry.VALUE: "hostname contains blah ",
                Entry.SRC: f"{source} entry #1/4",
                Entry.FLAGS: [Flags.LEFTB],
                Entry.WEIGHT: -1,
            },
            {
                Entry.TYPE: "simple",
                Entry.VALUE: "hostname contains blah ",
                Entry.SRC: f"{source} entry #2/4",
                Entry.FLAGS: [],
                Entry.WEIGHT: 1,
            },
            {
                Entry.TYPE: "simple",
                Entry.VALUE: "hostname contains blah",
                Entry.SRC: f"{source} entry #3/4",
                Entry.FLAGS: [Flags.RIGHTB],
                Entry.WEIGHT: 2,
            },
            {
                Entry.TYPE: "simple",
                Entry.VALUE: "hostname contains blah",
                Entry.SRC: f"{source} entry #4/4",
                Entry.FLAGS: [],
                Entry.WEIGHT: 0,
            },
        ]
        ret = wizard._parse_entries(entries=entries, source=source)
        assert ret == exp

    def test_invalid(self, wizard):
        entry1 = {
            Entry.TYPE: Types.SIMPLE,
            Entry.VALUE: f"{Flags.LEFTB}hostname contains blah ",
        }
        entry2 = {
            Entry.TYPE: "merp",
            Entry.VALUE: "hostname contains blah ",
        }

        entries = [entry1, entry2]
        source = "a test..."

        with pytest.raises(WizardError) as exc:
            wizard._parse_entries(entries=entries, source=source)
        assert f"Error parsing entry from {source}" in str(exc.value)
        assert "entry #2/2" in str(exc.value)


class TestParseSimple(TestWizard):
    def test_valid(self, wizard):
        field = wizard.APIOBJ.FIELD_SIMPLE
        entry = {
            Entry.TYPE: "simple",
            Entry.VALUE: f"{field} contains blah",
        }
        exp = {
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
            "field": field,
            "fieldType": "axonius",
            "filter": f'("{field}" == regex("blah", "i"))',
            "filteredAdapters": None,
            "leftBracket": False,
            "logicOp": "",
            "not": False,
            "rightBracket": False,
            "value": "blah",
        }
        ret = wizard._parse_simple(entry=entry, idx=0)
        assert ret == exp


class TestParseComplex(TestWizard):
    def test_valid(self, wizard):
        field = wizard.APIOBJ.FIELD_COMPLEX
        get_schema(apiobj=wizard.APIOBJ, field=field)
        sub = wizard.APIOBJ.FIELD_COMPLEX_SUB
        entry = {
            Entry.TYPE: "complex",
            Entry.VALUE: f"{field} // {sub} contains boom // {sub} exists",
        }
        exp = {
            "bracketWeight": 0,
            "children": [
                {
                    "condition": f'("{sub}" == regex("boom", "i"))',
                    "expression": {
                        "compOp": "contains",
                        "field": sub,
                        "filteredAdapters": None,
                        "value": "boom",
                    },
                    "i": 0,
                },
                {
                    "condition": f'(("{sub}" == ({{"$exists":true,"$ne":""}})))',
                    "expression": {
                        "compOp": "exists",
                        "field": sub,
                        "filteredAdapters": None,
                        "value": None,
                    },
                    "i": 1,
                },
            ],
            "compOp": "",
            "field": field,
            "fieldType": "axonius",
            "filter": (
                f'("{field}" == match([("{sub}" == regex("boom", "i")) and (("{sub}" == '
                '({"$exists":true,"$ne":""})))]))'
            ),
            "filteredAdapters": None,
            "leftBracket": False,
            "logicOp": "",
            "not": False,
            "rightBracket": False,
            "value": None,
            "context": "OBJ",
        }
        ret = wizard._parse_complex(entry=entry, idx=0)
        assert ret == exp

    def test_invalid(self, wizard):
        field = wizard.APIOBJ.FIELD_COMPLEX
        get_schema(apiobj=wizard.APIOBJ, field=field)

        sub = wizard.APIOBJ.FIELD_COMPLEX_SUB
        entry = {
            Entry.TYPE: "complex",
            Entry.VALUE: f"{field} // {sub} contains boom // badwolf exists",
        }
        with pytest.raises(WizardError) as exc:
            wizard._parse_complex(entry=entry, idx=0)
        assert "Unable to find SUB-FIELD" in str(exc.value)
        assert "Error parsing sub field" in str(exc.value)


class TestParseExprs(TestWizard):
    def test_valid1(self, wizard):
        field = wizard.APIOBJ.FIELD_SIMPLE
        entries = [
            {
                Entry.TYPE: "simple",
                Entry.VALUE: f"{field} contains blah",
            }
        ]
        exp = [
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
                "field": field,
                "fieldType": "axonius",
                "filter": f'("{field}" == regex("blah", "i"))',
                "filteredAdapters": None,
                "leftBracket": False,
                "logicOp": "",
                "not": False,
                "rightBracket": False,
                "value": "blah",
            }
        ]
        ret = wizard._parse_exprs(entries=entries)
        assert ret == exp

    def test_invalid(self, wizard):
        entry = {Entry.TYPE: "badwolf"}
        with pytest.raises(WizardError) as exc:
            wizard._parse_exprs(entries=[entry])
        assert "Error parsing expression from" in str(exc.value)


class TestParse(TestWizard, TestData):
    def test_valid(self, wizard, test_data1):
        entries, exp_exprs, exp_query = test_data1
        ret = wizard.parse(entries=entries)
        ret_query = ret[Results.QUERY]
        ret_exprs = ret[Results.EXPRS]
        assert ret_query == exp_query
        assert ret_exprs == exp_exprs

        # just make sure the REST API can parse the query
        wizard.APIOBJ.get(query=ret[Results.QUERY], max_rows=1)

        # make sure the REST API can create a saved query
        name = "api wizard test"

        try:
            wizard.APIOBJ.saved_query.delete_by_name(value=name)
        except Exception:
            pass

        sq = wizard.APIOBJ.saved_query.add(name=name, query=ret_query, expressions=ret_exprs)
        assert sq["name"] == name
        assert sq["view"]["query"]["filter"] == exp_query
        assert sq["view"]["query"]["expressions"] == exp_exprs

        wizard.APIOBJ.saved_query.delete_by_name(value=name)
