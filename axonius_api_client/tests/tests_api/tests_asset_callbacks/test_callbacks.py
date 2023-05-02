# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy
import io
import logging
import sys
import typing as t

import pytest

from axonius_api_client.api.asset_callbacks import Base, ExportMixins, get_callbacks_cls
from axonius_api_client.constants.api import FIELD_TRIM_LEN
from axonius_api_client.constants.fields import SCHEMAS_CUSTOM
from axonius_api_client.exceptions import ApiError

from ...utils import get_rows_exist, get_schema, log_check, random_string


def get_cbobj_main(
    apiobj, cbexport, getargs=None, state=None, store=None
) -> t.Union[Base, ExportMixins]:
    """Get a callback object."""
    state = state or {}
    getargs = getargs or {}
    store = store or {}

    cb_cls = get_callbacks_cls(export=cbexport)
    assert cb_cls.CB_NAME == cbexport

    cbobj = cb_cls(apiobj=apiobj, getargs=getargs, state=state, store=store)
    assert cbobj.CB_NAME == cbexport
    assert cbobj.APIOBJ == apiobj
    assert cbobj.STORE == store
    assert cbobj.STATE == state

    assert isinstance(cbobj.ALL_SCHEMAS, dict) and cbobj.ALL_SCHEMAS
    assert isinstance(cbobj.args_map(), dict)
    assert isinstance(cbobj.args_map_custom(), dict)
    assert isinstance(cbobj.args_strs, list)

    assert isinstance(cbobj.TAG_ROWS_ADD, list) and not cbobj.TAG_ROWS_ADD
    assert isinstance(cbobj.TAG_ROWS_REMOVE, list) and not cbobj.TAG_ROWS_REMOVE

    assert isinstance(cbobj.LOG, logging.Logger)

    assert "processor" in str(cbobj)
    assert "processor" in repr(cbobj)

    assert isinstance(cbobj.adapter_map, dict)
    assert cbobj.adapter_map

    assert isinstance(cbobj.schemas_selected, list)
    assert cbobj.schemas_selected
    for x in cbobj.schemas_selected:
        assert isinstance(x, dict)

    assert isinstance(cbobj.fields_selected, list)
    assert cbobj.fields_selected
    for x in cbobj.fields_selected:
        assert isinstance(x, str)

    return cbobj


@pytest.mark.slow
@pytest.mark.trylast
class Callbacks:
    """Base class for all tests for all callbacks."""

    @staticmethod
    def get_cbobj(apiobj, cbexport, getargs=None, state=None, store=None):
        """Get a callback object for testing."""
        return get_cbobj_main(
            apiobj=apiobj, cbexport=cbexport, getargs=getargs, state=state, store=store
        )


class CallbacksFull(Callbacks):
    """All tests for all callbacks."""

    def test_start_stop(self, cbexport, apiobj, caplog):
        getargs = {}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.start()
        log_check(caplog=caplog, entries=["Starting"], exists=True)

        cbobj.stop()
        log_check(caplog=caplog, entries=["Stopping"], exists=True)

    def test_add_report_adapters_missing_false(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs={"report_adapters_missing": False}
        )

        rows = cbobj.add_report_adapters_missing(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0] == original_row

        assert isinstance(cbobj.custom_schemas, list)
        assert not cbobj.custom_schemas

    def test_add_report_adapters_missing_true(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs={"report_adapters_missing": True}
        )

        rows = cbobj.add_report_adapters_missing(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert original_row != rows[0]

        assert isinstance(cbobj.custom_schemas, list)
        for field, schema in SCHEMAS_CUSTOM["report_adapters_missing"].items():
            assert schema["name_qual"] in test_row
            assert schema in cbobj.custom_schemas
            assert schema in cbobj.final_schemas

    def test_include_dates_false(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"include_dates": False})

        rows = cbobj.add_include_dates(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0] == original_row

        assert isinstance(cbobj.custom_schemas, list)
        assert not cbobj.custom_schemas

    def test_include_dates_true(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"include_dates": True})

        rows = cbobj.add_include_dates(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert original_row != rows[0]

        assert isinstance(cbobj.custom_schemas, list)
        for field, schema in SCHEMAS_CUSTOM["include_dates"].items():
            assert schema["name_qual"] in test_row
            assert schema in cbobj.custom_schemas
            assert schema in cbobj.final_schemas

    def test_echo_page_progress_0(self, cbexport, apiobj, caplog):
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"page_progress": 0},
            state={"rows_processed_total": 1, "rows_to_fetch_total": 10000},
        )
        cbobj.echo_page_progress()
        log_check(caplog=caplog, entries=["PROGRESS: "], exists=False)

    def test_echo_page_progress_1000_match_begin(self, cbexport, apiobj, caplog):
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"page_progress": 1000},
            state={"rows_processed_total": 1, "rows_to_fetch_total": 10000},
        )
        cbobj.echo_page_progress()
        log_check(caplog=caplog, entries=["PROGRESS: "], exists=True)

    def test_echo_page_progress_1000_match(self, cbexport, apiobj, caplog):
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"page_progress": 1000},
            state={"rows_processed_total": 1000, "rows_to_fetch_total": 10000},
        )
        cbobj.echo_page_progress()
        log_check(caplog=caplog, entries=["PROGRESS: "], exists=True)

    def test_echo_page_progress_1000_no_match(self, cbexport, apiobj, caplog):
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"page_progress": 1000},
            state={"rows_processed_total": 999, "rows_to_fetch_total": 10000},
        )
        cbobj.echo_page_progress()
        log_check(caplog=caplog, entries=["PROGRESS: "], exists=False)

    def test_do_add_null_values_true(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        original_row = copy.deepcopy(apiobj.COMPLEX_ROWS[0])
        picks = [x for x in original_row if x.startswith("specific_data.data.")]
        test_row = copy.deepcopy(original_row)
        test_row = {k: v for k, v in test_row.items() if k not in picks}

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [field_complex]},
            getargs={"field_null": True},
        )

        rows = cbobj.do_add_null_values(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        assert original_row != rows[0]

        for x in cbobj.schemas_selected:
            if x["name_qual"] in cbobj.GETARGS.get("field_excludes", []):
                continue
            assert x["name_qual"] in test_row

        for x in get_schema(apiobj=apiobj, field=field_complex, key="sub_fields"):
            for sub_value in test_row.get(field_complex) or []:
                if x["is_root"]:
                    assert x["name"] in sub_value
                else:
                    assert x["name"] not in sub_value

    def test_do_add_null_values_false(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)
        test_row.pop(apiobj.FIELD_ADAPTERS, None)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"field_null": False})

        rows = cbobj.do_add_null_values(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        if not cbobj.GETARGS["field_null"]:
            assert apiobj.FIELD_ADAPTERS not in rows[0]
            for k, v in original_row.items():
                if k != apiobj.FIELD_ADAPTERS:
                    assert rows[0][k] == v

    def test_do_add_null_values_exclude(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)
        test_row.pop(apiobj.FIELD_ADAPTERS, None)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"field_null": True, "field_excludes": [apiobj.FIELD_ADAPTERS]},
        )

        rows = cbobj.do_add_null_values(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        assert apiobj.FIELD_ADAPTERS not in rows[0]

    def test_do_custom_cb(self, cbexport, apiobj):
        # noinspection PyShadowingNames
        def cb1(self, rows):
            """Custom callback that modifies the rows."""
            for row in rows:
                self._row_idx = getattr(self, "_row_idx", 0)
                row["idcaps"] = row[apiobj.FIELD_AXON_ID].upper()
                row["idx"] = self._row_idx
                self._row_idx += 1
            return rows

        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"custom_cbs": [cb1]},
        )

        rows = cbobj.do_custom_cbs(rows=original_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        for idx, row in enumerate(rows):
            assert idx == row["idx"]
            assert row["idcaps"] == row[apiobj.FIELD_AXON_ID].upper()

    def test_do_custom_cb_fail(self, cbexport, apiobj):
        # noinspection PyShadowingNames
        def cb1(self, rows):
            """Fake custom callback that raises an exception."""
            raise ValueError(f"boom {self} {rows}")

        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"custom_cbs": [cb1]},
        )

        rows = cbobj.do_custom_cbs(rows=original_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert len(cbobj.CUSTOM_CB_EXC) == 1
        for x in cbobj.CUSTOM_CB_EXC:
            assert isinstance(x["exc"], ValueError)

    def test_process_tags_to_add_remove(self, cbexport, apiobj, caplog):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)
        row_id = test_row[apiobj.FIELD_AXON_ID]
        tags = [f"badwolf_{random_string(9)}", f"badwolf_{random_string(9)}"]
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"tags_add": tags})

        rows = cbobj.process_tags_to_add(rows=test_row)
        assert rows[0] == original_row
        assert {apiobj.FIELD_AXON_ID: row_id} in cbobj.TAG_ROWS_ADD

        cbobj.do_tagging()
        log_entries = ["tags.*assets"]
        log_check(caplog=caplog, entries=log_entries, exists=True)

        all_tags = apiobj.labels.get()
        wiz_entries = f"simple internal_axon_id equals {row_id}"
        row_refetch = apiobj.get(wiz_entries=wiz_entries, max_rows=1)[0]

        row_tags = row_refetch.get(apiobj.FIELD_TAGS, [])
        for tag in tags:
            assert tag in all_tags
            assert tag in row_tags

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"tags_remove": tags})

        rows = cbobj.process_tags_to_remove(rows=test_row)
        assert rows[0] == original_row
        assert {apiobj.FIELD_AXON_ID: row_id} in cbobj.TAG_ROWS_REMOVE

        cbobj.do_tagging()

        log_check(caplog=caplog, entries=["tags.*assets"], exists=True)

        row_refetch = apiobj.get(wiz_entries=wiz_entries, max_rows=1)[0]

        row_tags = row_refetch.get(apiobj.FIELD_TAGS, [])
        for tag in tags:
            assert tag not in row_tags

    def test_process_tags_to_add_empty(self, cbexport, apiobj, caplog):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"tags_add": []})

        rows = cbobj.process_tags_to_add(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0] == original_row
        assert not cbobj.TAG_ROWS_ADD
        cbobj.do_tagging()
        log_check(caplog=caplog, entries=["tags.*assets"], exists=False)

    def test_process_tags_to_remove_empty(self, cbexport, apiobj, caplog):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"tags_remove": []})

        rows = cbobj.process_tags_to_remove(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0] == original_row
        assert not cbobj.TAG_ROWS_REMOVE
        cbobj.do_tagging()
        log_check(caplog=caplog, entries=["tags.*assets"], exists=False)

    def test_do_excludes_empty(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"field_excludes": []})

        cbobj.do_excludes(rows=test_row)

        if not cbobj.GETARGS["field_excludes"]:
            assert test_row == original_row
        else:
            assert test_row != original_row

    def test_do_excludes(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        fields = [apiobj.FIELD_AXON_ID, apiobj.FIELD_ADAPTERS, "adapter_list_length"]

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"field_excludes": fields})

        rows = cbobj.do_excludes(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0] != original_row

        for field in fields:
            assert field not in test_row

    def test_do_excludes_sub(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        original_row = copy.deepcopy(apiobj.COMPLEX_ROWS[0])
        test_row = copy.deepcopy(original_row)

        sub_name = list(test_row[field_complex][0])[0]
        sub_exclude = f"{field_complex}.{sub_name}"
        excludes = [apiobj.FIELD_AXON_ID, sub_exclude]

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [*apiobj.fields_default, field_complex]},
            getargs={"field_excludes": excludes},
        )

        rows = cbobj.do_excludes(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0] != original_row

        for field in excludes:
            assert field not in test_row

        for item in test_row[field_complex]:
            assert sub_name not in item

    def test_do_join_values_true(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"field_join": True})
        rows = cbobj.do_join_values(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        assert original_row != test_row
        for field in original_row:
            if isinstance(original_row[field], list):
                assert isinstance(test_row[field], str)

    def test_do_join_values_false(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"field_join": False})
        rows = cbobj.do_join_values(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        if cbobj.GETARGS["field_join"]:
            assert original_row != test_row
        else:
            assert original_row == test_row

    def test_do_join_values_trim(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        original_row = copy.deepcopy(original_row)
        original_row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"field_join": True})

        rows = cbobj.do_join_values(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert original_row != test_row
        assert "TRIMMED" in test_row["test"]

        exp_len = FIELD_TRIM_LEN + 100
        test_len = len(test_row["test"])
        assert test_len <= exp_len

    def test_do_join_values_trim_disabled(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        original_row = copy.deepcopy(original_row)
        original_row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"field_join": True, "field_join_trim": 0},
        )

        rows = cbobj.do_join_values(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        assert original_row != test_row
        assert "TRIMMED" not in test_row["test"]

    def test_do_join_values_trim_custom_joiner(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        original_row = copy.deepcopy(original_row)
        original_row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"field_join": True, "field_join_value": "!!"},
        )

        rows = cbobj.do_join_values(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert original_row != test_row
        assert "!!" in test_row["test"]

    def test_do_change_field_titles_true(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        original_row = copy.deepcopy(apiobj.COMPLEX_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [field_complex]},
            getargs={"field_titles": True},
        )

        rows = cbobj.do_change_field_titles(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        assert sorted(list(original_row)) != sorted(list(test_row))

        for cb_schema in cbobj.final_schemas:
            assert cb_schema["column_title"] in test_row
            assert cb_schema["name"] not in test_row
            assert cb_schema["name_qual"] not in test_row

    def test_do_change_field_titles_false(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"field_titles": False})

        rows = cbobj.do_change_field_titles(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        if cbobj.GETARGS["field_titles"]:
            assert original_row != test_row
        else:
            assert original_row == test_row

    def test_do_flatten_fields_true(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        original_row = copy.deepcopy(apiobj.COMPLEX_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [field_complex]},
            getargs={"field_flatten": True},
        )

        rows = cbobj.do_flatten_fields(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert original_row != test_row
        assert field_complex not in test_row

        for sub_field in get_schema(apiobj=apiobj, field=field_complex, key="sub_fields"):
            if sub_field["is_root"]:
                assert sub_field["name_qual"] in test_row

        row_sub_fields = set()

        for field, value in original_row.items():
            if not isinstance(value, list) or not value:
                continue

            if not isinstance(value[0], dict):
                continue

            # make sure the original complex field got removed from the new row
            assert field not in test_row

            for sub_value in value:
                row_sub_fields.update(list(sub_value))

        for field, value in test_row.items():
            assert not isinstance(value, dict)

            if not isinstance(value, list):
                continue

            # assert no list items are complex
            assert not any([isinstance(i, (list, dict)) for i in value])

            if field not in original_row:
                # assert subfields from complex added to new row are fully qualified
                assert "specific_data.data." in field

            if field in original_row:
                continue

            if not any([field.endswith(x) for x in row_sub_fields]):
                assert all([x is None for x in value])

    def test_do_flatten_fields_exclude_sub(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        original_row = copy.deepcopy(apiobj.COMPLEX_ROWS[0])
        test_row = copy.deepcopy(original_row)

        sub_field = get_schema(apiobj=apiobj, field=field_complex, key="sub_fields")[0]
        sub_name = sub_field["name"]
        sub_exclude = f"{field_complex}.{sub_name}"
        excludes = [sub_exclude, apiobj.FIELD_AXON_ID]

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [*apiobj.fields_default, field_complex]},
            getargs={
                "field_flatten": True,
                "field_excludes": excludes,
            },
        )

        rows = cbobj.do_flatten_fields(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert original_row != test_row
        assert sub_field["name_qual"] not in test_row
        assert sub_name not in test_row
        for row in rows:
            for k, v in row.items():
                if isinstance(v, (list, tuple)):
                    for i in v:
                        assert not isinstance(i, dict)

    def test_do_flatten_fields_false(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        original_row = copy.deepcopy(apiobj.COMPLEX_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [field_complex]},
            getargs={"field_flatten": False},
        )

        rows = cbobj.do_flatten_fields(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        if cbobj.GETARGS["field_flatten"]:
            assert original_row != test_row
        else:
            assert original_row == test_row

    def test_do_flatten_fields_custom_null(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        original_row = copy.deepcopy(apiobj.COMPLEX_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [field_complex]},
            getargs={"field_flatten": True, "field_null_value": "badwolf"},
        )

        rows = cbobj.do_flatten_fields(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        assert original_row != test_row

        row_sub_fields = set()
        for field, value in original_row.items():
            if not isinstance(value, list) or not value:
                continue

            if not isinstance(value[0], dict):
                continue

            # make sure the original complex field got removed from the new row
            assert field not in test_row

            for sub_value in value:
                row_sub_fields.update(list(sub_value))

        for field, value in test_row.items():
            assert not isinstance(value, dict)

            if not isinstance(value, list):
                continue

            # assert no list items are complex
            assert not any([isinstance(i, (list, dict)) for i in value])

            if field not in original_row:
                # assert subfields from complex added to new row are fully qualified
                assert "specific_data.data." in field

            if field in original_row:
                continue

            if not any([field.endswith(x) for x in row_sub_fields]):
                assert all([x == "badwolf" for x in value])

    def test_do_explode_field_complex(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        original_row = copy.deepcopy(apiobj.COMPLEX_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [field_complex]},
            getargs={"field_explode": field_complex},
        )

        rows = cbobj.do_explode_field(rows=test_row)
        assert isinstance(rows, list)
        assert original_row not in rows
        for row in rows:
            assert field_complex not in row
            for sub_schema in cbobj.get_sub_schemas(schema=cbobj.schema_to_explode):
                assert sub_schema["name_qual"] in row

    def test_do_explode_field_simple(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        key = apiobj.FIELD_ADAPTERS
        row_val = test_row[key]
        row_val += ["test1", "test2"]
        row_len = len(row_val)
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"field_explode": key, "table_api_fields": True},
        )

        rows = cbobj.do_explode_field(rows=test_row)
        assert isinstance(rows, list)
        assert original_row not in rows
        assert len(rows) == row_len
        for idx, row in enumerate(rows):
            value = row[key]
            assert isinstance(value, str)
            assert value == row_val[idx]

    def test_do_explode_field_exclude(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={
                "field_explode": apiobj.FIELD_ADAPTERS,
                "field_excludes": [apiobj.FIELD_ADAPTERS],
            },
        )

        rows = cbobj.do_explode_field(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert test_row == rows[0]

    def test_do_explode_field_none(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport)

        rows = cbobj.do_explode_field(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert test_row == rows[0]

    def test_schema_to_explode_error(self, cbexport, apiobj):
        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs={"field_explode": "badwolf"}
        )
        with pytest.raises(ApiError):
            # noinspection PyStatementEffect
            cbobj.schema_to_explode

    def test_schema_to_explode_success(self, cbexport, apiobj):
        field = "adapters"
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"field_explode": field})
        schema = cbobj.schema_to_explode
        assert schema["name_qual"] == field

    def test_echo_ok_doecho_yes(self, cbexport, apiobj, capsys, caplog):
        entry = "badwolf"

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"do_echo": True})
        cbobj.echo(msg=entry)
        capture = capsys.readouterr()
        assert f"{entry}\n" in capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_debug_doecho_yes(self, cbexport, apiobj, capsys, caplog):
        entry = "badwolf"

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"do_echo": True})
        cbobj.echo(msg=entry, debug=True)
        capture = capsys.readouterr()
        assert f"{entry}\n" in capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_warning_doecho_yes(self, cbexport, apiobj, capsys, caplog):
        entry = "badwolf"

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"do_echo": True})
        cbobj.echo(msg=entry, warning=True)
        capture = capsys.readouterr()
        assert f"{entry}\n" in capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_error_doecho_yes(self, cbexport, apiobj, capsys, caplog):
        entry = "badwolf"

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"do_echo": True})
        with pytest.raises(SystemExit):
            cbobj.echo(msg=entry, error=ApiError)

        capture = capsys.readouterr()
        assert f"{entry}\n" in capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_ok_doecho_no(self, cbexport, apiobj, capsys, caplog):
        entry = "badwolf"

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"do_echo": False})
        cbobj.echo(msg=entry)
        capture = capsys.readouterr()
        if sys.version_info >= (3, 8, 0):
            assert not capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_error_doecho_no(self, cbexport, apiobj, capsys, caplog):
        entry = "badwolf"

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"do_echo": False})
        with pytest.raises(ApiError):
            cbobj.echo(msg=entry, error=ApiError)

        capture = capsys.readouterr()
        if capture.err:
            lines = capture.err.splitlines()
            for line in lines:
                assert line.startswith("ResourceWarning") or line.startswith("Exception ignored in")
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_error_doecho_yes_abort_no(self, cbexport, apiobj, capsys, caplog):
        entry = "badwolf"

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"do_echo": True})
        cbobj.echo(msg=entry, error=ApiError, abort=False)

        capture = capsys.readouterr()
        assert f"{entry}\n" in capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    # noinspection PyMethodMayBeStatic
    def test_get_callbacks_cls_error(self):
        with pytest.raises(ApiError):
            get_callbacks_cls(export="badwolf")

    def test_sw_whitelist_fail_no_sw_field(self, cbexport, apiobj):
        whitelist = ["chrome"]
        rows = copy.deepcopy(apiobj.ORIGINAL_ROWS)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"report_software_whitelist": whitelist},
        )

        for row in rows:
            with pytest.raises(ApiError):
                cbobj.add_report_software_whitelist(rows=row)

    def test_sw_whitelist(self, cbexport, api_devices):
        field = "specific_data.data.installed_software"
        whitelist = ["chrome"]
        get_schema(apiobj=api_devices, field=field)

        query = '(specific_data.data.installed_software.name == regex("chrome", "i"))'
        rows = api_devices.get(fields=field, query=query, max_rows=1)

        cbobj = self.get_cbobj(
            apiobj=api_devices,
            cbexport=cbexport,
            store={"fields_parsed": field},
            getargs={"report_software_whitelist": whitelist},
        )

        for row in rows:
            proc_rows = cbobj.add_report_software_whitelist(rows=row)
            assert isinstance(proc_rows, list)
            assert len(proc_rows) == 1
            for schema in SCHEMAS_CUSTOM["report_software_whitelist"].values():
                assert schema["name_qual"] in row
                assert field in row

    def test_do_field_compress_true(self, cbexport, apiobj):
        agg = "agg:id"
        specific = "active_directory:id"
        fields = [specific, agg]
        original_row = get_rows_exist(apiobj=apiobj, fields=fields)
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": fields},
            getargs={"field_compress": True, "field_titles": False},
        )

        rows = cbobj.do_change_field_compress(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        for row in rows:
            for field in fields:
                assert field in row
        for field in fields:
            assert field in cbobj.final_columns

    def test_do_field_replace_list_str(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"field_replace": [".=!!", "i="]},
        )

        assert cbobj.field_replacements == [[".", "!!"], ["i", ""]]

        for field in cbobj.final_columns:
            assert "." not in field
            assert "i" not in field

        rows = cbobj.do_change_field_replace(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        for row in rows:
            for key in row:
                assert "." not in key
                assert "i" not in key

    def test_do_field_replace_list_list(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"field_replace": [[".", "!!"], ["i", ""]]},
        )

        assert cbobj.field_replacements == [[".", "!!"], ["i", ""]]

        for field in cbobj.final_columns:
            assert "." not in field
            assert "i" not in field

        rows = cbobj.do_change_field_replace(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        for row in rows:
            for key in row:
                assert "." not in key
                assert "i" not in key

    def test_do_field_replace_bad_types(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"field_replace": [1, ["", ""]]},
        )

        assert cbobj.field_replacements == []

        rows = cbobj.do_change_field_replace(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert sorted(list(rows[0])) == sorted(list(original_row))

    def test_do_field_replace_str_missing_rhs(self, cbexport, apiobj):
        original_row = copy.deepcopy(apiobj.ORIGINAL_ROWS[0])
        test_row = copy.deepcopy(original_row)

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"field_replace": "."},
        )

        assert cbobj.field_replacements == [[".", ""]]

        rows = cbobj.do_change_field_replace(rows=test_row)
        assert isinstance(rows, list)
        assert len(rows) == 1

        for row in rows:
            for key in row:
                assert "." not in key


class Exports(Callbacks):
    """Tests for the exports class."""

    def test_fd_stdout_open_no_close(self, cbexport, apiobj):
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport)

        fd = cbobj.open_fd()

        assert fd == sys.stdout
        assert cbobj._fd == sys.stdout
        assert not cbobj._fd_close

        cbobj.close_fd()
        sys.stdout.write("should still work")

    def test_fd_custom_open_close_false(self, cbexport, apiobj):
        io_fd = io.StringIO()
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"export_fd": io_fd, "export_fd_close": False},
        )

        fd = cbobj.open_fd()

        assert fd == io_fd
        assert cbobj._fd == io_fd
        assert not cbobj._fd_close

        cbobj.close_fd()

        value = fd.getvalue()
        assert value == "\n"
        fd.write("")

    def test_fd_custom_open_close_true(self, cbexport, apiobj):
        io_fd = io.StringIO()

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"export_fd": io_fd, "export_fd_close": True},
        )

        fd = cbobj.open_fd()
        assert fd == io_fd
        assert cbobj._fd == io_fd
        assert cbobj._fd_close

        cbobj.close_fd()

        with pytest.raises(ValueError):
            fd.getvalue()

        with pytest.raises(ValueError):
            fd.write("")

    def test_fd_path_open_close_true(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.txt"

        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs={"export_file": export_file}
        )

        cbobj.open_fd()

        assert cbobj._file_path.name == export_file.name
        assert cbobj._file_mode == "Created new file"
        assert cbobj._fd_close

        cbobj.close_fd()
        assert export_file.is_file()
        assert export_file.read_text() == "\n"

        with pytest.raises(ValueError):
            cbobj._fd.write("")

    def test_fd_path_open_close_false(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.txt"

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"export_file": export_file, "export_fd_close": False},
        )

        cbobj.open_fd()

        assert cbobj._file_path.name == export_file.name
        assert cbobj._file_mode == "Created new file"
        assert not cbobj._fd_close

        cbobj.close_fd()
        assert export_file.is_file()
        cbobj._fd.write(" ")
        cbobj._fd.close()
        assert export_file.read_text() == "\n "

    def test_fd_path_backup_true(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.txt"
        export_file.touch()

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"export_file": export_file, "export_backup": True},
        )

        cbobj.open_fd()

        assert cbobj._file_path.name == export_file.name
        assert cbobj._file_mode == "Renamed existing file and created new file"
        assert cbobj._fd_close
        assert cbobj._file_path_backup.is_file()

        cbobj.close_fd()
        assert export_file.is_file()

    def test_fd_path_overwrite_true(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.txt"
        export_file.touch()

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"export_file": export_file, "export_overwrite": True},
        )

        cbobj.open_fd()

        assert cbobj._file_path.name == export_file.name
        assert cbobj._file_mode == "Overwrote existing file"
        assert cbobj._fd_close

        cbobj.close_fd()
        assert export_file.is_file()

    def test_fd_path_overwrite_false(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.txt"
        export_file.touch()

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"export_file": export_file, "export_overwrite": False},
        )

        with pytest.raises(ApiError):
            cbobj.open_fd()

    def test_export_file_create_dir_file(self, cbexport, apiobj, caplog, tmp_path):
        export_file = tmp_path / "badwolf" / "badwolf.txt"

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            getargs={"export_file": export_file},
        )
        cbobj.open_fd()

        cbobj.close_fd()
        assert export_file.is_file()
        assert export_file.parent.is_dir()
        log_check(
            caplog=caplog,
            entries=[
                "Created directory",
                "Created new file",
                "Exporting to.*Created new file",
            ],
            exists=True,
        )
