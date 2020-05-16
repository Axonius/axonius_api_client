# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import copy
import sys

from ...constants import (DEFAULT_PATH, FIELD_JOINER, FIELD_TRIM_LEN,
                          FIELD_TRIM_STR, SCHEMAS_CUSTOM)
from ...exceptions import ApiError
from ...tools import echo_error, echo_ok, get_path, listify


class Base:
    """Object for handling callbacks for assets."""

    CB_NAME = "base"
    FIND_KEYS = ["name", "name_qual", "column_title", "name_base"]

    def __init__(
        self, apiobj, fields, query=None, state=None, fields_map=None, getargs=None
    ):
        """Object for handling callbacks for assets."""
        self.LOG = apiobj.LOG.getChild(self.__class__.__name__)
        """:obj:`logging.Logger`: logger for this object."""

        self.APIOBJ = apiobj
        """:obj:`AssetMixin`: assets object."""

        apifields = [x for x in apiobj.FIELDS_API if x not in fields]
        self.SELECTED_FIELDS = apifields + fields
        """:obj:`list` of :obj:`str`: field names selected originally."""

        self.ALL_SCHEMAS = fields_map or apiobj.fields.get()
        """:obj:`dict`: map of adapter -> field schemas."""

        self.QUERY = query
        """:obj:`str`: query supplied to get assets method."""

        self.STATE = state or {}
        """:obj:`dict`: state dict used by get assets method to track paging."""

        self.GETARGS = getargs or {}
        """:obj:`dict`: original kwargs supplied to get assets method."""

        self.RAN = []
        """:obj:`list` of :obj:`str`: used by callbacks to see if they've run already."""

        self.TAG_ROWS_ADD = []
        """:obj:`list` of :obj:`dict`: assets to add tags to in do_tagging."""

        self.TAG_ROWS_REMOVE = []
        """:obj:`list` of :obj:`dict`: assets to remove tags from in do_tagging."""

    def start(self, **kwargs):
        """Run start callbacks."""
        join = "\n   - "
        self.echo(msg=f"Starting {self}")

        cbargs = ["{}={!r}".format(k, v) for k, v in self.GETARGS.items()]
        cbargs = "\n  " + "\n  ".join(cbargs)
        self.LOG.debug(f"Callback arguments: {cbargs}")

        config = join + join.join(self.args_strs)
        self.echo(msg=f"Configuration: {config}")
        self.echo(msg=f"Query: {self.QUERY}")

        columns_final = join + join.join(self.columns_final)
        self.echo(msg=f"Final columns: {columns_final}")

        schemas_pretty = self.APIOBJ.fields._prettify_schemas(
            schemas=self.schemas_selected
        )
        schemas_pretty = join + join.join(schemas_pretty)
        self.echo(msg=f"Selected Fields: {schemas_pretty}")

    def stop(self, **kwargs):
        """Run stop callbacks."""
        self.do_tagging()
        self.echo(msg=f"Stopping {self}")

    def _process_row(self, row):
        """Pass."""
        self.first_page()
        self.tags_add(row=row)
        self.tags_remove(row=row)
        self.report_adapters_missing(row=row)
        for schema in self.schemas_selected:
            self.do_excludes(row=row, schema=schema)
            self.do_nulls(row=row, schema=schema)
            self.do_flatten(row=row, schema=schema)

        new_rows = self.field_explode(row=row)

        for new_row in new_rows:
            self.field_join(row=new_row)
            self.field_titles(row=new_row)
        return new_rows

    def process_row(self, row):
        """Handle callbacks for an asset."""
        return self._process_row(row=row)

    def do_nulls(self, row, schema, key="name_qual"):
        """Null out missing fields."""
        if not self.GETARGS.get("field_null", False):
            return

        if self.is_excluded(schema=schema):
            return

        null_value = self.GETARGS.get("field_null_value", None)
        field = schema[key]

        if schema["is_complex"]:
            row[field] = listify(row.get(field, []))

            for item in row[field]:
                for sub_schema in schema["sub_fields"]:
                    if not self.is_excluded(schema=sub_schema) and sub_schema["is_root"]:
                        self.do_nulls(schema=sub_schema, row=item, key="name")
        else:
            row[field] = row.get(field, null_value)

    def do_excludes(self, row, schema):
        """Asset callback to remove fields from row."""
        if not self.GETARGS.get("field_excludes", []):
            return

        field_name = self.find_field_name(row=row, schema=schema)

        if not field_name or field_name not in row:
            return

        if self.is_excluded(schema=schema):
            row.pop(field_name)
            return

        if schema["is_complex"]:
            items = listify(row.get(field_name, []))
            for sub_schema in schema["sub_fields"]:
                if self.is_excluded(schema=sub_schema):
                    for item in items:
                        sub_field_name = self.find_field_name(
                            row=item, schema=sub_schema
                        )
                        item.pop(sub_field_name, None)

    def field_join(self, row):
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

    def field_titles(self, row):
        """Asset callback to change qual name to title."""
        if not self.GETARGS.get("field_titles", False):
            return

        for schema in self.schemas_final:
            field_name = self.find_field_name(row=row, schema=schema)
            if field_name:
                row[schema["column_title"]] = row.pop(field_name)

    def get_sub_schemas(self, schema):
        """Pass."""
        schemas = schema["sub_fields"]
        return [x for x in schemas if not self.is_excluded(schema=x) and x["is_root"]]

    def do_flatten(self, row, schema):
        """Asset callback to flatten complex fields."""
        if not self.GETARGS.get("field_flatten", False):
            return

        null_value = self.GETARGS.get("field_null_value", None)

        if (
            self.is_excluded(schema=schema)
            or not schema["is_complex"]
            or self.schema_to_explode == schema
        ):
            return

        sub_schemas = self.get_sub_schemas(schema=schema)

        if not sub_schemas:
            return

        items = listify(row.pop(schema["name_qual"], []))

        for sub_schema in sub_schemas:
            row[sub_schema["name_qual"]] = []

            for item in items:
                value = item.pop(sub_schema["name"], null_value)
                value = value if isinstance(value, list) else [value]
                row[sub_schema["name_qual"]] += value

    def find_field_name(self, row, schema):
        """Pass."""
        for key in self.FIND_KEYS:
            name = schema.get(key)
            if name and name in row:
                return name
        return ""

    def field_explode(self, row):
        """Explode a field into multiple rows."""
        explode = self.GETARGS.get("field_explode", "")
        if not explode:
            return [row]

        null_value = self.GETARGS.get("field_null_value", None)
        schema = self.schema_to_explode
        field_name = self.find_field_name(row=row, schema=schema)

        if not schema or not field_name or self.is_excluded(schema=schema):
            return [row]

        if len(listify(row.get(field_name))) <= 1:
            return [row]

        if schema["is_complex"]:
            sub_schemas = self.get_sub_schemas(schema=schema)
            if not sub_schemas:
                return [row]

            new_rows = {}
            items = listify(row.pop(field_name))

            for sub_schema in sub_schemas:
                for idx, item in enumerate(items):
                    new_rows.setdefault(idx, copy.deepcopy(row))
                    value = item.pop(sub_schema["name"], null_value)
                    new_rows[idx][sub_schema["name_qual"]] = value
        else:
            new_rows = {}
            items = listify(row.pop(field_name))

            for idx, item in enumerate(items):
                new_rows.setdefault(idx, copy.deepcopy(row))
                new_rows[idx][field_name] = item

        return [new_rows[idx] for idx in new_rows]

    @property
    def schemas_custom(self):
        """Pass."""
        schemas = []
        if self.GETARGS.get("report_adapters_missing", False):
            schemas += list(SCHEMAS_CUSTOM["report_adapters_missing"].values())
        return schemas

    @property
    def schemas_final(self):
        """Predict the future schemas that will be returned."""
        if hasattr(self, "_schemas_final"):
            return self._schemas_final

        flat = self.GETARGS.get("field_flatten", False)
        explode_field_name = self.schema_to_explode.get("name_qual", "")

        final = {}

        for schema in self.schemas_selected:
            if self.is_excluded(schema=schema):
                continue

            is_explode_field = schema["name_qual"] == explode_field_name
            if schema["is_complex"] and (is_explode_field or flat):
                for sub_schema in schema["sub_fields"]:
                    if self.is_excluded(schema=sub_schema) or not sub_schema["is_root"]:
                        continue

                    final[sub_schema["name_qual"]] = sub_schema
            else:
                final.setdefault(schema["name_qual"], schema)

        self._schemas_final = list(final.values())
        return self._schemas_final

    @property
    def columns_final(self):
        """Pass."""
        if hasattr(self, "_columns_final"):
            return self._columns_final

        use_titles = self.GETARGS.get("field_titles", False)
        self._columns_final = []

        for schema in self.schemas_final:
            if use_titles:
                name = schema["column_title"]
            else:
                name = schema["name_qual"]
            self._columns_final.append(name)

        return self._columns_final

    @property
    def schemas_selected(self):
        """Pass."""
        if hasattr(self, "_schemas_selected"):
            return self._schemas_selected

        self._schemas_selected = [] + self.schemas_custom

        all_schemas = self.ALL_SCHEMAS

        if isinstance(self.ALL_SCHEMAS, dict):
            all_schemas = []
            for schemas in self.ALL_SCHEMAS.values():
                all_schemas += schemas

        for field in self.SELECTED_FIELDS:
            for schema in all_schemas:
                name = schema["name_qual"]
                if name == field:
                    self._schemas_selected.append(schema)

        return self._schemas_selected

    @property
    def schema_to_explode(self):
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
    def adapter_map(self):
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

    def report_adapters_missing(self, row):
        """Pass."""
        if not self.GETARGS.get("report_adapters_missing", False):
            return

        use_titles = self.GETARGS.get("field_titles", False)
        schemas = SCHEMAS_CUSTOM["report_adapters_missing"]
        schema = schemas["adapters_missing"]

        key = "name_qual" if use_titles else "column_title"
        field_name = schema[key]

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

    def is_excluded(self, schema):
        """Check if a name supplied to field_excludes matches one of GET_SCHEMA_KEYS."""
        excludes = listify(self.GETARGS.get("field_excludes", []))

        for exclude in excludes:
            for key in self.FIND_KEYS:
                name = schema.get(key, None)
                if (name and exclude) and name == exclude:
                    return True
        return False

    def tags_add(self, row):
        """Pass."""
        tags = listify(self.GETARGS.get("tags_add", []))
        if not tags:
            return

        tag_row = {"internal_axon_id": row["internal_axon_id"]}

        if tag_row not in self.TAG_ROWS_ADD:
            self.TAG_ROWS_ADD.append(tag_row)

    def tags_remove(self, row):
        """Pass."""
        tags = listify(self.GETARGS.get("tags_remove", []))
        if not tags:
            return

        tag_row = {"internal_axon_id": row["internal_axon_id"]}

        if tag_row not in self.TAG_ROWS_REMOVE:
            self.TAG_ROWS_REMOVE.append(tag_row)

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

    def first_page(self):
        """Asset callback to echo first page info using an echo method."""
        if "first_page" in self.RAN:
            return

        self.RAN.append("first_page")

        rows_page = self.STATE.get("rows_fetched_this_page")
        rows_total = self.STATE.get("rows_to_fetch_total")
        page_total = self.STATE.get("pages_to_fetch_total")

        info = f"{rows_page} rows (total rows {rows_total}, total pages {page_total})"
        self.echo(msg=f"First page received {info}")

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

    def open_fd_stdout(self):
        """Pass."""
        self._file_path = None
        self._fd_close = False
        self._fd = sys.stdout
        self.echo(msg="Exporting to stdout")
        return self._fd

    def open_fd(self):
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
            self.echo(msg=f"Closing {self._fd}")
            self._fd.close()

    def echo(self, msg, error=None, level="info", level_error="error"):
        """Pass."""
        do_echo = self.GETARGS.get("do_echo", False)

        if do_echo:
            echo_error(msg) if error else echo_ok(msg)
            return

        if error:
            getattr(self.LOG, level_error)(msg)
            raise error(msg)

        getattr(self.LOG, level)(msg)

    @property
    def args_map(self):
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
        ]

    @property
    def args_strs(self):
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

    def __str__(self):
        """Show info for this object."""
        return f"{self.__class__.__name__} callbacks"

    def __repr__(self):
        """Show info for this object."""
        return self.__str__()
