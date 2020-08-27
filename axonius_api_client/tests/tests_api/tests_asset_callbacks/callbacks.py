# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy
import io
import logging
import sys

import pytest

from axonius_api_client.api.asset_callbacks import get_callbacks_cls
from axonius_api_client.constants import (
    AGG_ADAPTER_NAME,
    AGG_ADAPTER_TITLE,
    FIELD_TRIM_LEN,
    SCHEMAS_CUSTOM,
)
from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import TAGS
from ...utils import log_check


def load_test_data(apiobj):
    """Pass."""
    apiobj.TEST_DATA = getattr(apiobj, "TEST_DATA", {})

    if not apiobj.TEST_DATA.get("fields_map"):
        apiobj.TEST_DATA["fields_map"] = fields_map = apiobj.fields.get()

    if not apiobj.TEST_DATA.get("assets"):
        apiobj.TEST_DATA["assets"] = apiobj.get(max_rows=2000, fields_map=fields_map)

    if not apiobj.TEST_DATA.get("cb_assets"):
        field_complex = apiobj.TEST_DATA["field_complex"]
        try:
            apiobj.fields.get_field_name(value=field_complex)
        except NotFoundError:
            # XXX users no longer seem to have any complex field data as of 04/23/2020
            apiobj.TEST_DATA["field_complex"] = None
            apiobj.TEST_DATA["field_complexes"] = apiobj.fields_default
            apiobj.TEST_DATA["cb_assets_query"] = None

        field_complexes = apiobj.TEST_DATA["field_complexes"]
        cb_assets_query = apiobj.TEST_DATA["cb_assets_query"]
        apiobj.TEST_DATA["cb_assets"] = apiobj.get(
            query=cb_assets_query,
            max_rows=2000,
            fields=field_complexes,
            fields_map=fields_map,
        )

    return apiobj


class Callbacks:
    """Pass."""

    def get_cbobj(self, apiobj, cbexport, getargs=None, state=None, store=None):
        """Pass."""
        state = state or {}
        getargs = getargs or {}
        store = store or {}

        query = apiobj.TEST_DATA["cb_assets_query"]
        fields = apiobj.TEST_DATA["field_complexes"]

        store.setdefault("query", query)
        store.setdefault("fields", fields)

        cbcls = get_callbacks_cls(export=cbexport)
        assert cbcls.CB_NAME == cbexport

        cbobj = cbcls(
            apiobj=apiobj,
            fields_map=apiobj.TEST_DATA["fields_map"],
            getargs=getargs,
            state=state,
            store=store,
        )
        assert cbobj.CB_NAME == cbexport
        assert cbobj.APIOBJ == apiobj
        assert cbobj.ALL_SCHEMAS == apiobj.TEST_DATA["fields_map"]
        assert cbobj.STORE == store
        assert cbobj.STATE == state

        assert isinstance(cbobj.args_map, list)
        assert isinstance(cbobj.args_strs, list)

        assert isinstance(cbobj.TAG_ROWS_ADD, list) and not cbobj.TAG_ROWS_ADD
        assert isinstance(cbobj.TAG_ROWS_REMOVE, list) and not cbobj.TAG_ROWS_REMOVE

        assert isinstance(cbobj.LOG, logging.Logger)
        assert isinstance(cbobj.RAN, list)
        assert not cbobj.RAN

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

    def test_start_stop(self, cbexport, apiobj, caplog):
        """Pass."""
        getargs = {}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        assert not caplog.records

        cbobj.start()
        log_check(caplog=caplog, entries=["Starting"], exists=True)

        cbobj.stop()
        log_check(caplog=caplog, entries=["Stopping"], exists=True)

    def test_add_report_adapters_missing_false(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        report_schemas = SCHEMAS_CUSTOM["report_adapters_missing"]
        getargs = {"report_adapters_missing": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.add_report_adapters_missing(row=test_row)
        assert test_row == original_row

        assert isinstance(cbobj.custom_schemas, list)
        for field, schema in report_schemas.items():
            assert schema not in cbobj.custom_schemas

        assert not cbobj.custom_schemas

    def test_add_report_adapters_missing_true(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        report_schemas = SCHEMAS_CUSTOM["report_adapters_missing"]
        getargs = {"report_adapters_missing": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.add_report_adapters_missing(row=test_row)
        assert original_row != test_row

        assert isinstance(cbobj.custom_schemas, list)
        for field, schema in report_schemas.items():
            assert schema["name_qual"] in test_row
            assert schema in cbobj.custom_schemas
            assert schema in cbobj.final_schemas

    def test_echo_page_progress_0(self, cbexport, apiobj, caplog):
        """Pass."""
        getargs = {"page_progress": 0}
        state = {"rows_processed_total": 1, "rows_to_fetch_total": 10000}
        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs=getargs, state=state
        )
        log_entries = ["PROGRESS: "]

        cbobj.echo_page_progress()
        log_check(caplog=caplog, entries=log_entries, exists=False)

    def test_echo_page_progress_1000_match_begin(self, cbexport, apiobj, caplog):
        """Pass."""
        getargs = {"page_progress": 1000}
        state = {"rows_processed_total": 1, "rows_to_fetch_total": 10000}
        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs=getargs, state=state
        )
        log_entries = ["PROGRESS: "]

        cbobj.echo_page_progress()
        log_check(caplog=caplog, entries=log_entries, exists=True)

    def test_echo_page_progress_1000_match(self, cbexport, apiobj, caplog):
        """Pass."""
        getargs = {"page_progress": 1000}
        state = {"rows_processed_total": 1000, "rows_to_fetch_total": 10000}
        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs=getargs, state=state
        )
        log_entries = ["PROGRESS: "]

        cbobj.echo_page_progress()
        log_check(caplog=caplog, entries=log_entries, exists=True)

    def test_echo_page_progress_1000_no_match(self, cbexport, apiobj, caplog):
        """Pass."""
        getargs = {"page_progress": 1000}
        state = {"rows_processed_total": 999, "rows_to_fetch_total": 10000}
        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs=getargs, state=state
        )
        log_entries = ["PROGRESS: "]

        cbobj.echo_page_progress()
        log_check(caplog=caplog, entries=log_entries, exists=False)

    def test_do_add_null_values_true(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        picks = [x for x in original_row if x.startswith("specific_data.data.")][-1]
        original_row.pop(picks)
        test_row = copy.deepcopy(original_row)

        field_complex = apiobj.TEST_DATA["field_complex"]

        schema = apiobj.fields.get_field_schema(
            value=field_complex,
            schemas=apiobj.TEST_DATA["fields_map"][AGG_ADAPTER_NAME],
        )

        getargs = {"field_null": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_add_null_values(row=test_row, schema=cb_schema)

        assert original_row != test_row

        for schema in cbobj.schemas_selected:
            if schema["name_qual"] in cbobj.GETARGS.get("field_excludes", []):
                continue
            assert schema["name_qual"] in test_row

        if apiobj.TEST_DATA["has_complex"]:
            for sub_field in schema["sub_fields"]:
                for sub_value in test_row[field_complex]:
                    if sub_field["is_root"]:
                        assert sub_field["name"] in sub_value
                    else:
                        assert sub_field["name"] not in sub_value

    def test_do_add_null_values_false(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"field_null": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_add_null_values(row=test_row, schema=cb_schema)

        if not cbobj.GETARGS["field_null"]:
            assert original_row == test_row

    def test_do_add_null_values_exclude(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)
        test_row.pop("adapters", None)

        getargs = {"field_null": True, "field_excludes": ["adapters"]}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_add_null_values(row=test_row, schema=cb_schema)
        assert "adapters" not in test_row

    def test_process_tags_to_add(self, cbexport, apiobj, caplog):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)
        row_id = test_row["internal_axon_id"]

        getargs = {"tags_add": TAGS}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.process_tags_to_add(row=test_row)
        assert test_row == original_row
        assert {"internal_axon_id": row_id} in cbobj.TAG_ROWS_ADD

        cbobj.do_tagging()
        log_entries = ["tags.*assets"]
        log_check(caplog=caplog, entries=log_entries, exists=True)

        all_tags = apiobj.labels.get()
        row_refetch = apiobj.get_by_value(
            field="internal_axon_id", value=row_id, field_manual=True
        )[0]

        row_tags = row_refetch.get(apiobj.FIELD_TAGS, [])
        for tag in TAGS:
            assert tag in all_tags
            assert tag in row_tags

    def test_process_tags_to_remove(self, cbexport, apiobj, caplog):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)
        row_id = test_row["internal_axon_id"]

        getargs = {"tags_remove": TAGS}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.process_tags_to_remove(row=test_row)
        assert test_row == original_row
        assert {"internal_axon_id": row_id} in cbobj.TAG_ROWS_REMOVE

        cbobj.do_tagging()

        log_entries = ["tags.*assets"]
        log_check(caplog=caplog, entries=log_entries, exists=True)

        row_refetch = apiobj.get_by_value(
            field="internal_axon_id", value=row_id, field_manual=True
        )[0]

        row_tags = row_refetch.get(apiobj.FIELD_TAGS, [])
        for tag in TAGS:
            assert tag not in row_tags

    def test_process_tags_to_add_empty(self, cbexport, apiobj, caplog):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"tags_add": []}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.process_tags_to_add(row=test_row)
        assert test_row == original_row
        assert not cbobj.TAG_ROWS_ADD

        cbobj.do_tagging()

        log_entries = ["tags.*assets"]
        log_check(caplog=caplog, entries=log_entries, exists=False)

    def test_process_tags_to_remove_empty(self, cbexport, apiobj, caplog):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"tags_remove": []}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.process_tags_to_remove(row=test_row)
        assert test_row == original_row
        assert not cbobj.TAG_ROWS_REMOVE

        cbobj.do_tagging()

        log_entries = ["tags.*assets"]
        log_check(caplog=caplog, entries=log_entries, exists=False)

    def test_do_excludes_empty(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"field_excludes": []}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_excludes(row=test_row, schema=cb_schema)

        if not cbobj.GETARGS["field_excludes"]:
            assert test_row == original_row
        else:
            assert test_row != original_row

    def test_do_excludes(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        fields = ["internal_axon_id", "adapters", "adapters_list_length"]

        getargs = {"field_excludes": fields}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_excludes(row=test_row, schema=cb_schema)

        assert test_row != original_row

        for field in fields:
            assert field not in test_row

    def test_do_excludes_sub(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        field_complex = apiobj.TEST_DATA["field_complex"]

        sub_exclude = list(test_row[field_complex][0])[0]
        fields = ["internal_axon_id", sub_exclude]

        getargs = {"field_excludes": fields}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_excludes(row=test_row, schema=cb_schema)

        assert test_row != original_row

        for field in fields:
            assert field not in test_row

        for item in test_row[field_complex]:
            assert sub_exclude not in item

    def test_do_join_values_true(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"field_join": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.do_join_values(row=test_row)

        assert original_row != test_row
        for field in original_row:
            if isinstance(original_row[field], list):
                assert isinstance(test_row[field], str)

    def test_do_join_values_false(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"field_join": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.do_join_values(row=test_row)

        if cbobj.GETARGS["field_join"]:
            assert original_row != test_row
        else:
            assert original_row == test_row

    def test_do_join_values_trim(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        original_row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()
        test_row = copy.deepcopy(original_row)

        getargs = {"field_join": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.do_join_values(row=test_row)
        assert original_row != test_row
        assert "TRIMMED" in test_row["test"]

        exp_len = FIELD_TRIM_LEN + 100
        test_len = len(test_row["test"])
        assert test_len <= exp_len

    def test_do_join_values_trim_disabled(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        original_row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()
        test_row = copy.deepcopy(original_row)

        getargs = {"field_join": True, "field_join_trim": 0}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.do_join_values(row=test_row)
        assert original_row != test_row
        assert "TRIMMED" not in test_row["test"]

    def test_do_join_values_trim_custom_joiner(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        original_row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()
        test_row = copy.deepcopy(original_row)

        getargs = {"field_join": True, "field_join_value": "!!"}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.do_join_values(row=test_row)
        assert original_row != test_row
        assert "!!" in test_row["test"]

    def test_do_change_field_titles_true(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        row_titles = list(test_row)
        field_complex = apiobj.TEST_DATA["field_complex"]

        getargs = {"field_titles": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.do_change_field_titles(row=test_row)
        for cb_schema in cbobj.schemas_selected:
            cbobj.do_excludes(row=test_row, schema=cb_schema)
        assert test_row != original_row

        test_row_titles = list(test_row)
        assert row_titles != test_row_titles
        check_pre = f"{AGG_ADAPTER_TITLE}: "
        not_check_pre = "specific_data.data."
        for test_row_title in test_row_titles:
            if test_row_title == field_complex:
                continue
            assert check_pre in test_row_title
            assert not_check_pre not in test_row_title

    def test_do_change_field_titles_false(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"field_titles": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.do_change_field_titles(row=test_row)

        if cbobj.GETARGS["field_titles"]:
            assert original_row != test_row
        else:
            assert original_row == test_row

    def test_do_flatten_fields_true(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        field_complex = apiobj.TEST_DATA["field_complex"]

        schema = apiobj.fields.get_field_schema(
            value=field_complex,
            schemas=apiobj.TEST_DATA["fields_map"][AGG_ADAPTER_NAME],
        )
        sub_fields = schema["sub_fields"]
        sub_quals = [x["name_qual"] for x in sub_fields if x["is_root"]]

        getargs = {"field_flatten": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_flatten_fields(row=test_row, schema=cb_schema)

        assert original_row != test_row

        assert any([y for x in sub_quals for y in test_row[x]])
        assert schema["name_qual"] not in test_row

        row_sub_fields = set()

        for field, value in original_row.items():
            if not isinstance(value, list) or not value:
                continue

            if not isinstance(value[0], dict):
                continue

            # make sure the orginal complex field got removed from the new row
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
                # assert subfields from complex added to new row are fully qual'd
                assert "specific_data.data." in field

            if field in original_row:
                continue

            if not any([field.endswith(x) for x in row_sub_fields]):
                assert all([x is None for x in value])

    def test_do_flatten_fields_exclude_sub(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        field_complex = apiobj.TEST_DATA["field_complex"]

        schema = apiobj.fields.get_field_schema(
            value=field_complex,
            schemas=apiobj.TEST_DATA["fields_map"][AGG_ADAPTER_NAME],
        )
        sub_field = schema["sub_fields"][0]
        sub_field_name = sub_field["name"]
        sub_field_name_qual = sub_field["name_qual"]

        getargs = {
            "field_flatten": True,
            "field_excludes": [sub_field_name, "internal_axon_id"],
        }
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_flatten_fields(row=test_row, schema=cb_schema)

        assert original_row != test_row
        assert sub_field_name_qual not in test_row

    def test_do_flatten_fields_false(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"field_flatten": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_flatten_fields(row=test_row, schema=cb_schema)

        if cbobj.GETARGS["field_flatten"]:
            if apiobj.TEST_DATA["has_complex"]:
                assert original_row != test_row
            else:
                assert original_row == test_row
        else:
            assert original_row == test_row

    def test_do_flatten_fields_custom_null(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"field_flatten": True, "field_null_value": "badwolf"}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        for cb_schema in cbobj.schemas_selected:
            cbobj.do_flatten_fields(row=test_row, schema=cb_schema)

        row_sub_fields = set()
        assert original_row != test_row

        for field, value in original_row.items():
            if not isinstance(value, list) or not value:
                continue

            if not isinstance(value[0], dict):
                continue

            # make sure the orginal complex field got removed from the new row
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
                # assert subfields from complex added to new row are fully qual'd
                assert "specific_data.data." in field

            if field in original_row:
                continue

            if not any([field.endswith(x) for x in row_sub_fields]):
                assert all([x == "badwolf" for x in value])

    def test_do_explode_field_complex(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        field_complex = apiobj.TEST_DATA["field_complex"]

        getargs = {"field_explode": field_complex}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        new_rows = cbobj.do_explode_field(row=test_row)
        assert isinstance(new_rows, list)
        assert original_row not in new_rows
        for new_row in new_rows:
            assert field_complex not in new_row

    def test_do_explode_field_simple(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        key = "adapters"
        row_val = test_row[key]
        row_val += ["test1", "test2"]
        row_len = len(row_val)
        getargs = {"field_explode": key, "table_api_fields": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        new_rows = cbobj.do_explode_field(row=test_row)
        assert isinstance(new_rows, list)
        assert original_row not in new_rows
        assert len(new_rows) == row_len
        for idx, new_row in enumerate(new_rows):
            value = new_row[key]
            assert isinstance(value, str)
            assert value == row_val[idx]

    def test_do_explode_field_exclude(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {"field_explode": "adapters", "field_excludes": ["adapters"]}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        new_rows = cbobj.do_explode_field(row=test_row)
        assert isinstance(new_rows, list)
        assert len(new_rows) == 1
        assert test_row == new_rows[0]

    def test_do_explode_field_none(self, cbexport, apiobj):
        """Pass."""
        original_row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        test_row = copy.deepcopy(original_row)

        getargs = {}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        new_rows = cbobj.do_explode_field(row=test_row)
        assert isinstance(new_rows, list)
        assert len(new_rows) == 1
        assert test_row == new_rows[0]

    def test_schema_to_explode_error(self, cbexport, apiobj):
        """Pass."""
        getargs = {"field_explode": "badwolf"}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        with pytest.raises(ApiError):
            cbobj.schema_to_explode

    def test_schema_to_explode_success(self, cbexport, apiobj):
        """Pass."""
        field = "adapters"
        getargs = {"field_explode": field}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        schema = cbobj.schema_to_explode
        assert schema["name_qual"] == field

    def test_fd_stdout_open_no_close(self, cbexport, apiobj):
        """Pass."""
        getargs = {}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        fd = cbobj.open_fd()

        assert fd == sys.stdout
        assert cbobj._fd == sys.stdout
        assert not cbobj._fd_close

        cbobj.close_fd()
        sys.stdout.write("should still work")

    def test_fd_custom_open_close_false(self, cbexport, apiobj):
        """Pass."""
        io_fd = io.StringIO()

        getargs = {"export_fd": io_fd, "export_fd_close": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        fd = cbobj.open_fd()

        assert fd == io_fd
        assert cbobj._fd == io_fd
        assert not cbobj._fd_close

        cbobj.close_fd()

        value = fd.getvalue()
        assert value == "\n"
        fd.write("")

    def test_fd_custom_open_close_true(self, cbexport, apiobj):
        """Pass."""
        io_fd = io.StringIO()

        getargs = {"export_fd": io_fd, "export_fd_close": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

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
        """Pass."""
        export_file = tmp_path / "badwolf.txt"
        getargs = {"export_file": export_file}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.open_fd()

        assert cbobj._file_path.name == export_file.name
        assert cbobj._file_mode == "created"
        assert cbobj._fd_close

        cbobj.close_fd()
        assert export_file.is_file()
        assert export_file.read_text() == "\n"

        with pytest.raises(ValueError):
            cbobj._fd.write("")

    def test_fd_path_open_close_false(self, cbexport, apiobj, tmp_path):
        """Pass."""
        export_file = tmp_path / "badwolf.txt"
        getargs = {"export_file": export_file, "export_fd_close": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.open_fd()

        assert cbobj._file_path.name == export_file.name
        assert cbobj._file_mode == "created"
        assert not cbobj._fd_close

        cbobj.close_fd()
        assert export_file.is_file()
        cbobj._fd.write(" ")
        cbobj._fd.close()
        assert export_file.read_text() == "\n "

    def test_fd_path_overwrite_true(self, cbexport, apiobj, tmp_path):
        """Pass."""
        export_file = tmp_path / "badwolf.txt"
        export_file.touch()
        getargs = {"export_file": export_file, "export_overwrite": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        cbobj.open_fd()

        assert cbobj._file_path.name == export_file.name
        assert cbobj._file_mode == "overwrote"
        assert cbobj._fd_close

        cbobj.close_fd()
        assert export_file.is_file()

    def test_fd_path_overwrite_false(self, cbexport, apiobj, tmp_path):
        """Pass."""
        export_file = tmp_path / "badwolf.txt"
        export_file.touch()
        getargs = {"export_file": export_file, "export_overwrite": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        with pytest.raises(ApiError):
            cbobj.open_fd()

    def test_echo_ok_doecho_yes(self, cbexport, apiobj, capsys, caplog):
        """Pass."""
        entry = "xxxxxxx"

        getargs = {"do_echo": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.echo(msg=entry)
        capture = capsys.readouterr()
        assert f"{entry}\n" in capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_error_doecho_yes(self, cbexport, apiobj, capsys, caplog):
        """Pass."""
        entry = "xxxxxxx"

        getargs = {"do_echo": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        with pytest.raises(SystemExit):
            cbobj.echo(msg=entry, error=ApiError)

        capture = capsys.readouterr()
        assert f"{entry}\n" in capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_ok_doecho_no(self, cbexport, apiobj, capsys, caplog):
        """Pass."""
        entry = "xxxxxxx"

        getargs = {"do_echo": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.echo(msg=entry)
        capture = capsys.readouterr()
        assert not capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_echo_error_doecho_no(self, cbexport, apiobj, capsys, caplog):
        """Pass."""
        entry = "xxxxxxx"

        getargs = {"do_echo": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        with pytest.raises(ApiError):
            cbobj.echo(msg=entry, error=ApiError)

        capture = capsys.readouterr()
        assert not capture.err
        assert not capture.out
        log_check(caplog=caplog, entries=[entry], exists=True)

    def test_get_callbacks_cls_error(self):
        """Pass."""
        with pytest.raises(ApiError):
            get_callbacks_cls(export="badwolf")
