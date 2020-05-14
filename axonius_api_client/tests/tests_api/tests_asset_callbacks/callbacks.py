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

    def get_cbobj(self, apiobj, cbexport, getargs=None):
        """Pass."""
        state = {
            "max_pages": None,
            "max_rows": None,
            "page_cursor": None,
            "page_left": 0,
            "page_num": 1,
            "page_size": 2000,
            "page_sleep": 0,
            "page_total": 0,
            "rows_fetched": 0,
            "rows_page": 0,
            "rows_processed": 0,
            "rows_start": 0,
            "rows_total": 0,
            "time_fetch": 0,
            "time_page": 0,
            "use_cursor": False,
        }
        getargs = getargs or {}
        query = apiobj.TEST_DATA["cb_assets_query"]
        fields = apiobj.TEST_DATA["field_complexes"]
        cbcls = get_callbacks_cls(export=cbexport)
        assert cbcls.CB_NAME == cbexport

        cbobj = cbcls(
            apiobj=apiobj,
            fields_map=apiobj.TEST_DATA["fields_map"],
            getargs=getargs,
            fields=fields,
            query=query,
            state=state,
        )
        assert cbobj.CB_NAME == cbexport
        assert cbobj.APIOBJ == apiobj
        assert cbobj.FIELDS_MAP == apiobj.TEST_DATA["fields_map"]
        assert cbobj.FIELDS == fields
        assert cbobj.QUERY == query
        assert cbobj.GETARGS == getargs
        assert cbobj.STATE == state

        assert isinstance(cbobj.args_map, list)
        assert isinstance(cbobj.args_strs, list)

        assert isinstance(cbobj.TAG_ROWS_ADD, list) and not cbobj.TAG_ROWS_ADD
        assert isinstance(cbobj.TAG_ROWS_REMOVE, list) and not cbobj.TAG_ROWS_REMOVE

        assert isinstance(cbobj.LOG, logging.Logger)
        assert isinstance(cbobj.RAN, list)
        assert not cbobj.RAN

        assert cbobj.__class__.__name__ in str(cbobj)
        assert cbobj.__class__.__name__ in repr(cbobj)

        assert isinstance(cbobj.SCHEMAS_ALL, list)
        assert cbobj.SCHEMAS_ALL

        assert isinstance(cbobj.adapter_map, dict)
        assert cbobj.adapter_map

        assert isinstance(cbobj.SCHEMAS_FIELDS, list)
        assert cbobj.SCHEMAS_FIELDS
        for schema in cbobj.SCHEMAS_FIELDS:
            assert schema in cbobj.SCHEMAS_ALL

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

    def test_report_adapters_missing_false(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        report_schemas = SCHEMAS_CUSTOM["report_adapters_missing"]
        getargs = {"report_adapters_missing": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.report_adapters_missing(row=copy.deepcopy(row))
        assert isinstance(row_ret, dict)
        assert row == row_ret

        assert isinstance(cbobj.SCHEMAS_CUSTOM, list)
        for field, schema in report_schemas.items():
            assert schema not in cbobj.SCHEMAS_CUSTOM

        assert not cbobj.SCHEMAS_CUSTOM

    def test_report_adapters_missing_true(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        report_schemas = SCHEMAS_CUSTOM["report_adapters_missing"]
        getargs = {"report_adapters_missing": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.report_adapters_missing(row=copy.deepcopy(row))
        assert isinstance(row_ret, dict)
        assert row != row_ret

        assert isinstance(cbobj.SCHEMAS_CUSTOM, list)
        for field, schema in report_schemas.items():
            assert schema["name_qual"] in row_ret
            assert schema in cbobj.SCHEMAS_CUSTOM
            assert schema in cbobj.schemas_final(flat=False)
            assert schema in cbobj.schemas_final(flat=True)

    def test_firstpage(self, cbexport, apiobj, caplog):
        """Pass."""
        getargs = {"first_page": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        log_entries = ["First page "]

        cbobj.first_page()
        assert "first_page" in cbobj.RAN
        log_check(caplog=caplog, entries=log_entries, exists=True)

        caplog.clear()
        cbobj.first_page()
        log_check(caplog=caplog, entries=log_entries, exists=False)

    def test_field_null_true(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        field_complex = apiobj.TEST_DATA["field_complex"]

        field_complexes = apiobj.TEST_DATA["field_complexes"]

        schema = apiobj.fields.get_field_schema(
            value=field_complex,
            schemas=apiobj.TEST_DATA["fields_map"][AGG_ADAPTER_NAME],
        )

        getargs = {"field_null": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_null(row=copy.deepcopy(row))
        assert isinstance(row_ret, dict)
        assert row != row_ret

        for field in field_complexes:
            assert field in row_ret

        if apiobj.TEST_DATA["has_complex"]:
            for sub_field in schema["sub_fields"]:
                for sub_value in row_ret[field_complex]:
                    if sub_field["is_root"]:
                        assert sub_field["name"] in sub_value
                    else:
                        assert sub_field["name"] not in sub_value

    def test_field_null_false(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        getargs = {"field_null": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_null(row=copy.deepcopy(row))
        assert isinstance(row_ret, dict)
        assert row == row_ret

    def test_field_null_exclude(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        row.pop("adapters", None)
        getargs = {"field_null": True, "field_excludes": ["adapters"]}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_null(row=copy.deepcopy(row))
        assert isinstance(row_ret, dict)
        assert "adapters" not in row_ret

    def test_tags_add(self, cbexport, apiobj, caplog):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        row_id = row["internal_axon_id"]

        getargs = {"tags_add": TAGS}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.tags_add(row=copy.deepcopy(row))
        assert row == row_ret
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

    def test_tags_remove(self, cbexport, apiobj, caplog):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        row_id = row["internal_axon_id"]

        getargs = {"tags_remove": TAGS}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.tags_remove(row=copy.deepcopy(row))
        assert row == row_ret
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

    def test_tags_add_empty(self, cbexport, apiobj, caplog):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"tags_add": []}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.tags_add(row=copy.deepcopy(row))
        assert row == row_ret
        assert not cbobj.TAG_ROWS_ADD

        cbobj.do_tagging()

        log_entries = ["tags.*assets"]
        log_check(caplog=caplog, entries=log_entries, exists=False)

    def test_tags_remove_empty(self, cbexport, apiobj, caplog):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"tags_remove": []}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.tags_remove(row=copy.deepcopy(row))
        assert row == row_ret
        assert not cbobj.TAG_ROWS_REMOVE

        cbobj.do_tagging()

        log_entries = ["tags.*assets"]
        log_check(caplog=caplog, entries=log_entries, exists=False)

    def test_field_excludes_empty(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"field_excludes": []}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_excludes(row=copy.deepcopy(row))
        assert row == row_ret

    def test_field_excludes(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        fields = ["internal_axon_id", "adapters", "adapters_list_length"]

        getargs = {"field_excludes": fields}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_excludes(row=copy.deepcopy(row))
        assert row != row_ret

        for field in fields:
            assert field not in row_ret

    def test_field_excludes_sub(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        field_complex = apiobj.TEST_DATA["field_complex"]

        sub_exclude = list(row[field_complex][0])[0]
        fields = ["internal_axon_id", sub_exclude]

        getargs = {"field_excludes": fields}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_excludes(row=copy.deepcopy(row))
        assert row != row_ret

        for field in fields:
            assert field not in row_ret

        for item in row_ret[field_complex]:
            assert sub_exclude not in item

    def test_field_join_true(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"field_join": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_join(row=copy.deepcopy(row))

        assert row != row_ret
        for field in row:
            if isinstance(row[field], list):
                assert isinstance(row_ret[field], str)

    def test_field_join_false(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"field_join": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_join(row=copy.deepcopy(row))
        assert row == row_ret

    def test_field_join_trim(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()

        getargs = {"field_join": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_join(row=copy.deepcopy(row))
        assert row != row_ret
        assert "TRIMMED" in row_ret["test"]

        exp_len = FIELD_TRIM_LEN + 100
        test_len = len(row_ret["test"])
        assert test_len <= exp_len

    def test_field_join_trim_disabled(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()

        getargs = {"field_join": True, "field_join_trim": 0}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_join(row=copy.deepcopy(row))
        assert row != row_ret
        assert "TRIMMED" not in row_ret["test"]

    def test_field_join_trim_custom_joiner(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        row["test"] = ("aaaa " * (FIELD_TRIM_LEN + 1000)).split()

        getargs = {"field_join": True, "field_join_value": "!!"}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_join(row=copy.deepcopy(row))
        assert row != row_ret
        assert "!!" in row_ret["test"]

    def test_field_titles_true(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        row_titles = list(row)

        getargs = {"field_titles": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_titles(row=copy.deepcopy(row))
        assert row != row_ret

        row_ret_titles = list(row_ret)
        assert row_titles != row_ret_titles
        for x in row_ret_titles:
            assert f"{AGG_ADAPTER_TITLE}: " in x
            assert "specific_data.data." not in x

    def test_field_titles_false(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"field_titles": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_titles(row=copy.deepcopy(row))
        assert row == row_ret

    def test_field_flatten_true(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        field_complex = apiobj.TEST_DATA["field_complex"]

        schema = apiobj.fields.get_field_schema(
            value=field_complex,
            schemas=apiobj.TEST_DATA["fields_map"][AGG_ADAPTER_NAME],
        )
        sub_fields = schema["sub_fields"]
        sub_quals = [x["name_qual"] for x in sub_fields if x["is_root"]]

        getargs = {"field_flatten": True}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_flatten(row=copy.deepcopy(row))
        assert row != row_ret

        assert any([y for x in sub_quals for y in row_ret[x]])
        assert schema["name_qual"] not in row_ret

        row_sub_fields = set()

        for field, value in row.items():
            if not isinstance(value, list) or not value:
                continue

            if not isinstance(value[0], dict):
                continue

            # make sure the orginal complex field got removed from the new row
            assert field not in row_ret

            for sub_value in value:
                row_sub_fields.update(list(sub_value))

        for field, value in row_ret.items():
            assert not isinstance(value, dict)

            if not isinstance(value, list):
                continue

            # assert no list items are complex
            assert not any([isinstance(i, (list, dict)) for i in value])

            if field not in row:
                # assert subfields from complex added to new row are fully qual'd
                assert "specific_data.data." in field

            if field in row:
                continue

            if not any([field.endswith(x) for x in row_sub_fields]):
                assert all([x is None for x in value])

    def test_field_flatten_exclude_sub(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
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

        row_ret = cbobj.field_flatten(row=copy.deepcopy(row))
        assert row != row_ret
        assert sub_field_name_qual not in row_ret

    def test_field_flatten_false(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"field_flatten": False}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_flatten(row=copy.deepcopy(row))
        assert row == row_ret

    def test_field_flatten_custom_null(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"field_flatten": True, "field_null_value": "badwolf"}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_flatten(row=copy.deepcopy(row))

        row_sub_fields = set()
        assert row != row_ret

        for field, value in row.items():
            if not isinstance(value, list) or not value:
                continue

            if not isinstance(value[0], dict):
                continue

            # make sure the orginal complex field got removed from the new row
            assert field not in row_ret

            for sub_value in value:
                row_sub_fields.update(list(sub_value))

        for field, value in row_ret.items():
            assert not isinstance(value, dict)

            if not isinstance(value, list):
                continue

            # assert no list items are complex
            assert not any([isinstance(i, (list, dict)) for i in value])

            if field not in row:
                # assert subfields from complex added to new row are fully qual'd
                assert "specific_data.data." in field

            if field in row:
                continue

            if not any([field.endswith(x) for x in row_sub_fields]):
                assert all([x == "badwolf" for x in value])

    def test_field_explode_complex(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        field_complex = apiobj.TEST_DATA["field_complex"]

        getargs = {"field_explode": field_complex}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_explode(row=copy.deepcopy(row))
        assert isinstance(row_ret, list)
        assert row != row_ret
        assert len(row) > len(row_ret)
        for row_x in row_ret:
            assert field_complex not in row_x

    def test_field_explode_simple(self, cbexport, apiobj):
        """Pass."""
        key = "adapters"
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])
        row_val = row["adapters"]
        row_len = len(row_val)
        getargs = {"field_explode": key}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_explode(row=copy.deepcopy(row))
        assert isinstance(row_ret, list)
        assert row != row_ret
        assert len(row_ret) == row_len
        for idx, row_x in enumerate(row_ret):
            value = row_x[key]
            assert isinstance(value, str)
            assert value == row_val[idx]

    def test_field_explode_exclude(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {"field_explode": "adapters", "field_excludes": ["adapters"]}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_explode(row=copy.deepcopy(row))
        assert isinstance(row_ret, list)
        assert len(row_ret) == 1
        assert row == row_ret[0]

    def test_field_explode_none(self, cbexport, apiobj):
        """Pass."""
        row = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][0])

        getargs = {}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)

        row_ret = cbobj.field_explode(row=copy.deepcopy(row))
        assert isinstance(row_ret, list)
        assert len(row_ret) == 1
        assert row == row_ret[0]

    def test_field_explode_schema_error(self, cbexport, apiobj):
        """Pass."""
        getargs = {"field_explode": "badwolf"}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        with pytest.raises(ApiError):
            cbobj.explode_schema

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
