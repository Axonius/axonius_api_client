# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import copy
import logging
import re
import sys
from typing import IO, Generator, List, Optional

from ...constants import (
    DEFAULT_PATH,
    FIELD_JOINER,
    FIELD_TRIM_LEN,
    FIELD_TRIM_STR,
    SCHEMAS_CUSTOM,
)
from ...exceptions import ApiError
from ...tools import (
    calc_percent,
    echo_error,
    echo_ok,
    echo_warn,
    get_path,
    join_kv,
    listify,
)


class Base:
    """Object for handling callbacks for assets."""

    CB_NAME: str = "base"
    FIND_KEYS: List[str] = ["name", "name_qual", "column_title", "name_base"]

    def __init__(
        self,
        apiobj,
        store: dict,
        state: Optional[dict] = None,
        fields_map: Optional[dict] = None,
        getargs: dict = None,
    ):
        """Object for handling callbacks for assets."""
        self.LOG: logging.Logger = apiobj.LOG.getChild(self.__class__.__name__)
        """logger for this object."""

        self.APIOBJ = apiobj
        """:obj:`AssetMixin`: assets object."""

        self.ALL_SCHEMAS: dict = fields_map or apiobj.fields.get()
        """Map of adapter -> field schemas."""

        self.STATE: dict = state or {}
        """state dict used by get assets method to track paging."""

        self.STORE: dict = store or {}
        """store dict used by get assets method to track arguments."""

        self.GETARGS: dict = getargs or {}
        """original kwargs supplied to get assets method."""

        self.RAN: List[str] = []
        """used by callbacks to see if they've run already."""

        self.TAG_ROWS_ADD: List[dict] = []
        """assets to add tags to in do_tagging."""

        self.TAG_ROWS_REMOVE: List[dict] = []
        """assets to remove tags from in do_tagging."""

        self._init()

    def _init(self):
        """Pass."""
        pass

    def start(self, **kwargs):
        """Run start callbacks."""
        join = "\n   - "
        self.echo(msg=f"Starting {self}")

        cbargs = join + join.join(join_kv(obj=self.GETARGS))
        self.LOG.debug(f"Get Extra Arguments: {cbargs}")

        config = join + join.join(self.args_strs)
        self.echo(msg=f"Configuration: {config}")

        store = join + join.join(join_kv(obj=self.STORE))
        self.echo(msg=f"Get Arguments: {store}")

        schemas_pretty = self.APIOBJ.fields._prettify_schemas(
            schemas=self.schemas_selected
        )
        schemas_pretty = join + join.join(schemas_pretty)
        self.echo(msg=f"Selected Columns: {schemas_pretty}")

        final_columns = join + join.join(self.final_columns)
        self.echo(msg=f"Final Columns: {final_columns}")

    def stop(self, **kwargs):
        """Run stop callbacks."""
        self.do_tagging()
        self.echo(msg=f"Stopping {self}")

    def process_row(self, row: dict) -> List[dict]:
        """Handle callbacks for an asset."""
        self.do_pre_row()
        return self.do_row(row=row)

    def do_pre_row(self):
        """Pass."""
        self.STATE.setdefault("rows_processed_total", 0)
        self.STATE["rows_processed_total"] += 1
        self.echo_page_progress()

    def do_row(self, row: dict) -> List[dict]:
        """Pass."""
        custom_cbs = listify(self.GETARGS.get("custom_cbs", []))

        for custom_cb in custom_cbs:
            try:
                custom_cb(self=self, row=row)
            except Exception as exc:
                msg = f"Custom callback {custom_cb} failed: {exc}"
                self.echo(msg=msg, error="exception", abort=False)

        self.process_tags_to_add(row=row)
        self.process_tags_to_remove(row=row)
        self.add_report_adapters_missing(row=row)
        self.add_report_software_whitelist(row=row)

        for schema in self.schemas_selected:
            self.do_excludes(row=row, schema=schema)
            self.do_add_null_values(row=row, schema=schema)
            self.do_flatten_fields(row=row, schema=schema)

        new_rows = self.do_explode_field(row=row)
        for new_row in new_rows:
            self.do_join_values(row=new_row)
            self.do_change_field_titles(row=new_row)

        return new_rows

    def echo_page_progress(self):
        """Asset callback to echo progress per N rows using an echo method."""
        page_progress = self.GETARGS.get("page_progress", 10000)
        if not page_progress or not isinstance(page_progress, int):
            return

        proc = self.STATE.get("rows_processed_total", 0) or 0
        total = self.STATE.get("rows_to_fetch_total", 0) or 0
        taken = self.STATE.get("fetch_seconds_total", 0) or 0
        page_total = self.STATE.get("pages_to_fetch_total", 0) or 0
        page_num = self.STATE.get("page_number", 0) or 0

        if not ((proc % page_progress == 0) or (proc >= total) or (proc <= 1)):
            return

        percent = calc_percent(part=proc, whole=total)
        percent = f"{percent:.2f}%"
        percent = f"{percent:>7}"

        total_len = len(str(total))
        rows = f"[ROWS: {proc:>{total_len}} / {total}]"

        page_total_len = len(str(page_total))
        pages = f"[PAGES: {page_num:>{page_total_len}} / {page_total}]"

        taken = f"{taken:.2f} seconds so far"

        self.echo(msg=f"PROGRESS: {percent} {rows} {pages} in {taken}")

    def do_add_null_values(self, row: dict, schema: dict, key: str = "name_qual"):
        """Null out missing fields."""
        if not self.GETARGS.get("field_null", False) or self.is_excluded(schema=schema):
            return

        null_value = self.GETARGS.get("field_null_value", None)
        field = schema[key]

        if schema["is_complex"]:
            row[field] = listify(row.get(field, []))

            for item in row[field]:
                for sub_schema in self.get_sub_schemas(schema=schema):
                    self.do_add_null_values(schema=sub_schema, row=item, key="name")
        else:
            row[field] = row.get(field, null_value)

    def do_excludes(self, row: dict, schema: dict):
        """Asset callback to remove fields from row."""
        if not self.GETARGS.get("field_excludes", []):
            return

        if self.is_excluded(schema=schema):
            row.pop(schema["name_qual"], None)
            return

        if schema["is_complex"]:
            items = listify(row.get(schema["name_qual"], []))
            for sub_schema in schema["sub_fields"]:
                if self.is_excluded(schema=sub_schema):
                    for item in items:
                        item.pop(sub_schema["name"], None)

    def do_join_values(self, row: dict):
        """Join values."""
        if not self.GETARGS.get("field_join", False):
            return

        joiner = str(self.GETARGS.get("field_join_value", FIELD_JOINER))
        trim_len = self.GETARGS.get("field_join_trim", FIELD_TRIM_LEN)
        trim_str = FIELD_TRIM_STR

        for field in row:
            if isinstance(row[field], list):
                row[field] = joiner.join([str(x) for x in row[field]])

            if trim_len and isinstance(row[field], str):
                field_len = len(row[field])
                if len(row[field]) >= trim_len:
                    msg = trim_str.format(field_len=field_len, trim_len=trim_len)
                    row[field] = joiner.join([row[field][:trim_len], msg])

    def do_change_field_titles(self, row: dict):
        """Asset callback to change qual name to title."""
        if not self.GETARGS.get("field_titles", False):
            return

        for schema in self.final_schemas:
            row[schema["column_title"]] = row.pop(schema["name_qual"], None)

    def do_flatten_fields(self, row: dict, schema: dict):
        """Asset callback to flatten complex fields."""
        if not self.GETARGS.get("field_flatten", False):
            return

        if self.schema_to_explode == schema:
            return

        self._do_flatten_fields(row=row, schema=schema)

    def _do_flatten_fields(self, row: dict, schema: dict):
        """Pass."""
        if self.is_excluded(schema=schema):
            return

        if not schema["is_complex"]:
            return

        null_value = self.GETARGS.get("field_null_value", None)

        items = listify(row.pop(schema["name_qual"], []))

        for sub_schema in self.get_sub_schemas(schema=schema):
            row[sub_schema["name_qual"]] = []

            for item in items:
                value = item.pop(sub_schema["name"], null_value)
                value = value if isinstance(value, list) else [value]
                row[sub_schema["name_qual"]] += value

    def do_explode_field(self, row: dict) -> List[dict]:
        """Explode a field into multiple rows."""
        explode = self.GETARGS.get("field_explode", "")
        null_value = self.GETARGS.get("field_null_value", None)

        if not explode:
            return [row]

        schema = self.schema_to_explode

        if self.is_excluded(schema=schema):
            return [row]

        original_row = copy.deepcopy(row)

        if schema["is_complex"]:
            new_rows_map = {}
            items = listify(row.pop(schema["name_qual"], []))

            for sub_schema in self.get_sub_schemas(schema=schema):
                for idx, item in enumerate(items):
                    new_rows_map.setdefault(idx, copy.deepcopy(row))
                    value = item.pop(sub_schema["name"], null_value)
                    new_rows_map[idx][sub_schema["name_qual"]] = value
        else:
            new_rows_map = {}
            items = listify(row.pop(schema["name_qual"], []))

            for idx, item in enumerate(items):
                new_rows_map.setdefault(idx, copy.deepcopy(row))
                new_rows_map[idx][schema["name_qual"]] = item

        new_rows = [new_rows_map[idx] for idx in new_rows_map]

        if not new_rows:
            self._do_flatten_fields(row=original_row, schema=schema)
            return [original_row]

        return new_rows

    def do_tagging(self):
        """Pass."""
        self.do_tag_add()
        self.do_tag_remove()

    def do_tag_add(self):
        """Pass."""
        tags_add = listify(self.GETARGS.get("tags_add", []))
        rows_add = self.TAG_ROWS_ADD
        if tags_add and rows_add:
            self.echo(msg=f"Adding tags {tags_add} to {len(rows_add)} assets")
            self.APIOBJ.labels.add(rows=rows_add, labels=tags_add)

    def do_tag_remove(self):
        """Pass."""
        tags_remove = listify(self.GETARGS.get("tags_remove", []))
        rows_remove = self.TAG_ROWS_REMOVE
        if tags_remove and rows_remove:
            self.echo(msg=f"Removing tags {tags_remove} from {len(rows_remove)} assets")
            self.APIOBJ.labels.remove(rows=rows_remove, labels=tags_remove)

    def process_tags_to_add(self, row: dict):
        """Pass."""
        tags = listify(self.GETARGS.get("tags_add", []))
        if not tags:
            return

        tag_row = {"internal_axon_id": row["internal_axon_id"]}

        if tag_row not in self.TAG_ROWS_ADD:
            self.TAG_ROWS_ADD.append(tag_row)

    def process_tags_to_remove(self, row: dict):
        """Pass."""
        tags = listify(self.GETARGS.get("tags_remove", []))
        if not tags:
            return

        tag_row = {"internal_axon_id": row["internal_axon_id"]}

        if tag_row not in self.TAG_ROWS_REMOVE:
            self.TAG_ROWS_REMOVE.append(tag_row)

    def add_report_software_whitelist(self, row: dict):
        """Pass."""

        def whitelist_match(whitelist, sw):
            name = sw.get("name", "")
            for whitelist_entry in whitelist:
                if re.search(whitelist_entry, name, re.I):
                    return True
            return False

        def sw_match(whitelist_entry, sws):
            for sw in sws:
                name = sw.get("name", "")
                if re.search(whitelist_entry, name, re.I):
                    return True
            return False

        def clean_list(obj):
            return sorted(list(set(obj)))

        if not self.GETARGS.get("report_software_whitelist", []):
            return

        sw_field = "specific_data.data.installed_software"

        if sw_field not in self.fields_selected:
            msg = f"Must include field (column) {sw_field!r}"
            self.echo(msg=msg, error=ApiError, level="error")

        schemas = SCHEMAS_CUSTOM["report_software_whitelist"]
        software_missing_schema = schemas["software_missing"]
        software_missing_name = software_missing_schema["name_qual"]

        software_whitelist_schema = schemas["software_whitelist"]
        software_whitelist_name = software_whitelist_schema["name_qual"]

        software_extra_schema = schemas["software_extra"]
        software_extra_name = software_extra_schema["name_qual"]

        installed_software = listify(row.get(sw_field, []))
        whitelist = self.GETARGS.get("report_software_whitelist", [])

        row[software_extra_name] = clean_list(
            [
                x.get("name")
                for x in installed_software
                if x.get("name") and not whitelist_match(whitelist=whitelist, sw=x)
            ]
        )

        row[software_missing_name] = clean_list(
            [
                x
                for x in whitelist
                if not sw_match(whitelist_entry=x, sws=installed_software)
            ]
        )

        row[software_whitelist_name] = whitelist

    def add_report_adapters_missing(self, row: dict):
        """Pass."""
        if not self.GETARGS.get("report_adapters_missing", False):
            return

        schemas = SCHEMAS_CUSTOM["report_adapters_missing"]
        schema = schemas["adapters_missing"]

        field_name = schema["name_qual"]

        adapters_row = row.get("adapters", [])
        adapter_map = self.adapter_map
        missing = []

        for adapter in adapter_map["all"]:
            if adapter in adapters_row:
                continue

            if adapter not in adapter_map["all_fields"]:
                continue

            if adapter not in missing:
                missing.append(adapter)

        row[field_name] = missing

    def is_excluded(self, schema: dict) -> bool:
        """Check if a name supplied to field_excludes matches one of GET_SCHEMA_KEYS."""
        excludes = listify(self.GETARGS.get("field_excludes", []))

        for exclude in excludes:
            for key in self.FIND_KEYS:
                name = schema.get(key, None)
                if (name and exclude) and name == exclude:
                    return True
        return False

    def open_fd_arg(self):
        """Pass."""
        self._fd = self.GETARGS["export_fd"]
        self._fd_close = self.GETARGS.get("export_fd_close", False)
        self.echo(msg=f"Exporting to {self._fd}")
        return self._fd

    def open_fd_path(self):
        """Pass."""
        self._export_file = self.GETARGS.get("export_file", None)
        self._export_path = self.GETARGS.get("export_path", DEFAULT_PATH)
        self._export_overwrite = self.GETARGS.get("export_overwrite", False)

        file_path = get_path(obj=self._export_path)
        file_path.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._file_path = fp = (file_path / self._export_file).resolve()

        if self._file_path.exists():
            self._file_mode = "overwrote"
            mode = "overwriting"
        else:
            self._file_mode = "created"
            mode = "creating"

        if self._file_path.exists() and not self._export_overwrite:
            msg = f"Export file '{fp}' already exists and overwite is False!"
            self.echo(msg=msg, error=ApiError, level="error")

        self._file_path.touch(mode=0o600)
        self._fd_close = self.GETARGS.get("export_fd_close", True)
        self._fd = self._file_path.open(mode="w", encoding="utf-8")
        self.echo(msg=f"Exporting to file '{fp}' ({mode})")
        return self._fd

    def open_fd_stdout(self) -> IO:
        """Pass."""
        self._file_path = None
        self._fd_close = False
        self._fd = sys.stdout
        self.echo(msg="Exporting to stdout")
        return self._fd

    def open_fd(self) -> IO:
        """Open a file descriptor."""
        if "export_fd" in self.GETARGS:
            self.open_fd_arg()
        elif self.GETARGS.get("export_file", None):
            self.open_fd_path()
        else:
            self.open_fd_stdout()
        return self._fd

    def close_fd(self):
        """Close a file descriptor."""
        self._fd.write("\n")
        if getattr(self, "_fd_close", False):
            name = str(getattr(self._fd, "name", self._fd))
            self.echo(msg=f"Finished exporting to {name!r}")
            self._fd.close()

    def echo(
        self,
        msg: str,
        error: bool = False,
        warning: bool = False,
        level: str = "info",
        level_error: str = "error",
        level_warning: str = "warning",
        abort: bool = True,
    ):
        """Pass."""
        do_echo = self.GETARGS.get("do_echo", False)

        if do_echo:
            if warning:
                echo_warn(msg=msg)
            elif error:
                echo_error(msg=msg, abort=abort)
            else:
                echo_ok(msg=msg)
            return

        if warning:
            getattr(self.LOG, level_warning)(msg)
        elif error:
            getattr(self.LOG, level_error)(msg)
            if abort:
                raise error(msg)
        else:
            getattr(self.LOG, level)(msg)

    def get_sub_schemas(self, schema: dict) -> Generator[dict, None, None]:
        """Pass."""
        sub_schemas = schema["sub_fields"]
        for sub_schema in sub_schemas:
            if self.is_excluded(schema=sub_schema) or not sub_schema["is_root"]:
                continue
            yield sub_schema

    @property
    def custom_schemas(self) -> List[dict]:
        """Pass."""
        schemas = []
        if self.GETARGS.get("report_adapters_missing", False):
            schemas += list(SCHEMAS_CUSTOM["report_adapters_missing"].values())
        if self.GETARGS.get("report_software_whitelist", False):
            schemas += list(SCHEMAS_CUSTOM["report_software_whitelist"].values())
        return schemas

    @property
    def final_schemas(self) -> List[dict]:
        """Predict the future schemas that will be returned."""
        if hasattr(self, "_final_schemas"):
            return self._final_schemas

        flat = self.GETARGS.get("field_flatten", False)
        explode_field_name = self.schema_to_explode.get("name_qual", "")

        final = {}

        for schema in self.schemas_selected:
            if self.is_excluded(schema=schema):
                continue

            is_explode_field = schema["name_qual"] == explode_field_name
            if schema["is_complex"] and (is_explode_field or flat):
                for sub_schema in self.get_sub_schemas(schema=schema):
                    final[sub_schema["name_qual"]] = sub_schema
            else:
                final.setdefault(schema["name_qual"], schema)

        self._final_schemas = list(final.values())
        return self._final_schemas

    @property
    def final_columns(self) -> List[str]:
        """Pass."""
        if hasattr(self, "_final_columns"):
            return self._final_columns

        use_titles = self.GETARGS.get("field_titles", False)
        key = "column_title" if use_titles else "name_qual"
        self._final_columns = [x[key] for x in self.final_schemas]

        return self._final_columns

    @property
    def fields_selected(self) -> List[str]:
        """Pass."""
        if hasattr(self, "_fields_selected"):
            return self._fields_selected

        include_details = self.STORE.get("include_details", False)

        fields = listify(self.STORE.get("fields", []))
        api_fields = [x for x in self.APIOBJ.FIELDS_API if x not in fields]

        if include_details:
            api_fields += ["meta_data.client_used", "unique_adapter_names_details"]

        self._fields_selected = []

        for field in api_fields + fields:
            self._fields_selected.append(field)
            if include_details and not field.startswith("adapters_data."):
                field_details = f"{field}_details"
                self._fields_selected.append(field_details)

        return self._fields_selected

    @property
    def schemas_selected(self) -> List[dict]:
        """Pass."""
        if hasattr(self, "_schemas_selected"):
            return self._schemas_selected

        self._schemas_selected = [] + self.custom_schemas

        all_schemas = self.ALL_SCHEMAS

        if isinstance(self.ALL_SCHEMAS, dict):
            all_schemas = []
            for schemas in self.ALL_SCHEMAS.values():
                all_schemas += schemas

        all_schemas_map = {x["name_qual"]: x for x in all_schemas}

        for field in self.fields_selected:
            if field in all_schemas_map:
                self._schemas_selected.append(all_schemas_map[field])
            else:
                msg = f"No schema found for field {field}"
                self.echo(msg=msg, warning=True)

        return self._schemas_selected

    @property
    def schema_to_explode(self) -> dict:
        """Pass."""
        if hasattr(self, "_schema_to_explode"):
            return self._schema_to_explode

        explode = self.GETARGS.get("field_explode", "")

        self._schema_to_explode = {}

        if not explode:
            return self._schema_to_explode

        valids = []

        for schema in self.schemas_selected:
            for key in self.FIND_KEYS:
                name = schema.get(key)
                if name:
                    valids.append(name)
                    if name == explode:
                        self._schema_to_explode = schema
                        return self._schema_to_explode

        valids = sorted(list(set(valids)))
        msg = f"Explode field {explode!r} not found, valid fields:{valids}"
        self.echo(msg=msg, error=ApiError)

    @property
    def adapter_map(self) -> dict:
        """Pass."""
        self._adapters_meta = getattr(self, "_adapters_meta", self.APIOBJ.adapters.get())
        amap = {
            "has_cnx": [],
            "all": [],
            "all_fields": [f"{x}_adapter" for x in self.ALL_SCHEMAS],
        }

        for adapter in self._adapters_meta:
            name_raw = adapter["name_raw"]

            if adapter not in amap["all"]:
                amap["all"].append(name_raw)
            if adapter["cnx"]:
                amap["has_cnx"].append(name_raw)

        amap = {k: list(v) for k, v in amap.items()}
        return amap

    @property
    def args_map(self) -> List[list]:
        """Pass."""
        return [
            ["field_excludes", "Exclude fields:", []],
            ["field_flatten", "Flatten complex fields:", False],
            ["field_explode", "Explode field:", None],
            ["field_titles", "Rename fields to titles:", False],
            ["field_join", "Join field values:", False],
            ["field_join_value", "Join field values using:", FIELD_JOINER],
            ["field_join_trim", "Join field character limit:", FIELD_TRIM_LEN],
            ["field_null", "Add missing fields:", False],
            ["field_null_value", "Missing field value:", None],
            ["tags_add", "Add tags:", []],
            ["tags_remove", "Remove tags:", []],
            ["report_adapters_missing", "Report Missing Adapters:", False],
            ["export_file", "Export to file:", None],
            ["export_path", "Export file to path:", DEFAULT_PATH],
            ["export_overwrite", "Export overwrite file:", False],
            ["export_schema", "Export schema:", False],
            ["page_progress", "Progress per row count:", 10000],
            ["json_flat", "Produce flat json:", False],
        ]

    @property
    def args_strs(self) -> List[str]:
        """Pass."""
        lines = []
        for arg, text, default in self.args_map:
            value = self.GETARGS.get(arg, default)
            if isinstance(value, str):
                value = repr(value)
            if isinstance(value, list):
                value = ", ".join(value)
                value = value or None
            lines.append(f"{text:30}{value}")
        return lines

    def __str__(self) -> str:
        """Show info for this object."""
        return f"{self.CB_NAME.upper()} processor"

    def __repr__(self) -> str:
        """Show info for this object."""
        return self.__str__()
