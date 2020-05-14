# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import copy
import sys

from ...constants import (DEFAULT_PATH, FIELD_JOINER, FIELD_TRIM_LEN,
                          FIELD_TRIM_STR, GET_SCHEMA_KEYS, SCHEMAS_CUSTOM)
from ...exceptions import ApiError
from ...tools import echo_error, echo_ok, get_path, listify


def custom_schemas(**kwargs):
    """Pass."""
    schemas = []
    if kwargs.get("report_adapters_missing", False):
        schemas += list(SCHEMAS_CUSTOM["report_adapters_missing"].values())
    return schemas


class Base:
    """Object for handling callbacks for assets."""

    CB_NAME = "base"

    def __init__(
        self, apiobj, fields, query=None, state=None, fields_map=None, getargs=None
    ):
        """Object for handling callbacks for assets."""
        self.LOG = apiobj.LOG.getChild(self.__class__.__name__)
        """:obj:`logging.Logger`: logger for this object."""

        self.APIOBJ = apiobj
        """:obj:`AssetMixin`: assets object."""

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

        self.FIELDS = [x for x in apiobj.FIELDS_API if x not in fields] + fields
        """:obj:`list` of :obj:`str`: field names selected originally."""

        self.FIELDS_MAP = fields_map or apiobj.fields.get()
        """:obj:`dict`: map of adapter -> field schemas."""

        self.SCHEMAS_CUSTOM = custom_schemas(**self.GETARGS)
        """:obj:`list` of :obj:`dict`: schemas of custom fields."""

        self.SCHEMAS_ALL = [y for x in self.FIELDS_MAP.values() for y in x]
        """:obj:`list` of :obj:`dict`: field schemas for all adapters."""

        self.SCHEMAS_FIELDS = [self.get_schema(value=x) for x in self.FIELDS]
        """:obj:`list` of :obj:`dict`: schemas of fields selected originally."""

    def get_schema(self, value, schemas=None, qual_only=True, **kwargs):
        """Pass."""
        if qual_only:
            kwargs["keys"] = ["name_qual"]
        schemas = schemas or (self.SCHEMAS_ALL + self.SCHEMAS_CUSTOM)
        return self.APIOBJ.fields.get_field_schema(
            value=value, schemas=schemas, **kwargs
        )

    def schemas_final_complex(self, schema, final):
        """Pass."""
        sub_schemas = self.filter_sub_schemas(schema=schema)
        final.update({x["name_qual"]: x for x in sub_schemas})

    def schemas_final_simple(self, schema, final):
        """Pass."""
        final.setdefault(schema["name_qual"], schema)

    def do_schemas_final(self, schema, explode, flat, final):
        """Pass."""
        if schema["is_complex"] and (schema["name_qual"] == explode or flat):
            self.schemas_final_complex(schema=schema, final=final)
        else:
            self.schemas_final_simple(schema=schema, final=final)

    def schemas_final(self, flat=False):
        """Predict the future schemas that will be returned."""
        flat = True if self.GETARGS.get("field_flatten", False) else flat

        schemas = self.filter_schemas(schemas=self.SCHEMAS_FIELDS)

        explode = self.explode_schema.get("name_qual", "")

        final = {}

        for schema in schemas:
            self.do_schemas_final(schema=schema, explode=explode, flat=flat, final=final)

        final = list(final.values())
        final += self.SCHEMAS_CUSTOM
        return final

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

        schemas = self.SCHEMAS_FIELDS
        schemas_pretty = self.APIOBJ.fields._prettify_schemas(schemas=schemas)
        schemas_pretty = join + join.join(schemas_pretty)
        self.echo(msg=f"Fields: {schemas_pretty}")

    def stop(self, **kwargs):
        """Run stop callbacks."""
        self.do_tagging()
        self.echo(msg=f"Stopping {self}")

    def row(self, row):
        """Handle callbacks for an asset."""
        self.first_page()
        row = self.tags_add(row=row)
        row = self.tags_remove(row=row)
        row = self.report_adapters_missing(row=row)
        row = self.field_null(row=row)
        row = self.field_excludes(row=row)
        rows = self.field_explode(row=row)
        rows = [self.field_flatten(row=x) for x in rows]
        rows = [self.field_join(row=x) for x in rows]
        rows = [self.field_titles(row=x) for x in rows]
        return rows

    def field_null(self, row):
        """Asset callback to add None values to fields not returned."""
        if not self.GETARGS.get("field_null", False):
            return row

        for schema in self.SCHEMAS_FIELDS:
            self.do_null(field=schema["name_qual"], row=row, schema=schema)
        return row

    def null_complex(self, row, field, schema):
        """Pass."""
        row[field] = listify(row.get(field, []))
        for entry in row[field]:
            sub_schemas = self.filter_sub_schemas(schema=schema)
            for sub_schema in sub_schemas:
                self.do_null(field=sub_schema["name"], schema=sub_schema, row=entry)

    def null_simple(self, row, field, schema):
        """Pass."""
        null_value = self.GETARGS.get("field_null_value", None)
        row[field] = row.get(field, null_value)

    def do_null(self, row, field, schema):
        """Null out missing fields."""
        if self.is_excluded(schema=schema):
            return

        if schema["is_complex"]:
            self.null_complex(row=row, field=field, schema=schema)
        else:
            self.null_simple(row=row, field=field, schema=schema)

    def exclude_complex_sub(self, row, field, items, schema):
        """Pass."""
        if self.is_excluded(schema=schema):
            for item in items:
                item.pop(schema["name"], None)

    def exclude_complex(self, row, field, schema):
        """Pass."""
        if schema["is_complex"]:
            sub_schemas = schema["sub_fields"]
            items = listify(row.get(field, []))
            for sub_schema in sub_schemas:
                self.exclude_complex_sub(
                    row=row, field=field, items=items, schema=sub_schema
                )

    def exclude_simple(self, row, field, schema):
        """Pass."""
        if not schema["is_complex"] and self.is_excluded(schema=schema):
            row.pop(field, None)

    def do_exclude(self, row, field, schema):
        """Pass."""
        self.exclude_simple(row=row, field=field, schema=schema)
        self.exclude_complex(row=row, field=field, schema=schema)

    def field_excludes(self, row):
        """Asset callback to remove fields from row."""
        if not self.GETARGS.get("field_excludes", []):
            return row

        for field in list(row):
            schema = self.get_schema(value=field)
            self.do_exclude(row=row, field=field, schema=schema)

        return row

    def field_join(self, row):
        """Join values."""
        if not self.GETARGS.get("field_join", False):
            return row

        joiner = self.GETARGS.get("field_join_value", FIELD_JOINER)
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
        return row

    def field_titles(self, row):
        """Asset callback to change qual name to title."""
        if not self.GETARGS.get("field_titles", False):
            return row

        for field in list(row):
            schema = self.get_schema(value=field)
            row[schema["column_title"]] = row.pop(field)
        return row

    def flatten_complex_sub(self, row, field, items, schema):
        """Asset callback to flatten complex fields."""
        null_value = self.GETARGS.get("field_null_value", None)
        sub_name = schema["name"]
        sub_name_qual = schema["name_qual"]
        row[sub_name_qual] = []
        for item in items:
            value = item.pop(sub_name, null_value)
            value = value if isinstance(value, list) else [value]
            row[sub_name_qual] += value

    def flatten_complex(self, row, field, schema):
        """Asset callback to flatten complex fields."""
        if schema["is_complex"] and not self.is_excluded(schema=schema):
            items = listify(row.pop(field, []))
            sub_schemas = self.filter_sub_schemas(schema=schema)
            for sub_schema in sub_schemas:
                self.flatten_complex_sub(
                    row=row, field=field, items=items, schema=sub_schema
                )

    def field_flatten(self, row):
        """Asset callback to flatten complex fields."""
        if not self.GETARGS.get("field_flatten", False):
            return row

        for field in list(row):
            schema = self.get_schema(value=field)
            self.flatten_complex(row=row, field=field, schema=schema)
        return row

    def explode_complex_sub(self, row, rows, items, schema):
        """Pass."""
        null_value = self.GETARGS.get("field_null_value", None)
        sub_name = schema["name"]
        sub_name_qual = schema["name_qual"]

        for idx, item in enumerate(items):
            rows.setdefault(idx, copy.deepcopy(row))
            rows[idx][sub_name_qual] = item.pop(sub_name, null_value)

    def explode_complex(self, row, rows, field, schema):
        """Explode a field into multiple rows."""
        items = listify(row.pop(field))
        sub_schemas = self.filter_sub_schemas(schema=schema)

        for sub_schema in sub_schemas:
            self.explode_complex_sub(row=row, rows=rows, items=items, schema=sub_schema)

    def explode_simple(self, row, rows, field, schema):
        """Explode a field into multiple rows."""
        items = listify(row.pop(field))

        for idx, item in enumerate(items):
            rows.setdefault(idx, copy.deepcopy(row))
            rows[idx][field] = item

    def do_explode(self, row, rows, field, schema):
        """Pass."""
        if schema["is_complex"]:
            self.explode_complex(row=row, rows=rows, field=field, schema=schema)
        else:
            self.explode_simple(row=row, rows=rows, field=field, schema=schema)

    def field_explode(self, row):
        """Explode a field into multiple rows."""
        explode = self.GETARGS.get("field_explode", "")

        if not explode:
            return [row]

        schema = self.explode_schema
        is_excluded = self.is_excluded(schema=schema)
        field = schema["name_qual"]
        if is_excluded or row.get(field, None) in [None, []] or field not in row:
            return [row]

        rows = {}
        self.do_explode(row=row, rows=rows, field=field, schema=schema)
        return [rows[idx] for idx in sorted(rows)]

    @property
    def explode_schema(self):
        """Pass."""
        explode = self.GETARGS.get("field_explode", "")
        if not explode:
            return {}

        valids = []

        for schema in self.SCHEMAS_FIELDS:
            names = [schema[x] for x in GET_SCHEMA_KEYS]
            if explode in names:
                return schema
            valids += names

        msg = f"Explode field {explode!r} not found, valid fields:{valids}"
        self.echo(msg=msg, error=ApiError)

    @property
    def adapter_map(self):
        """Pass."""
        self._adapters_meta = getattr(self, "_adapters_meta", self.APIOBJ.adapters.get())
        amap = {
            "has_cnx": [],
            "all": [],
            "all_fields": [f"{x}_adapter" for x in self.FIELDS_MAP],
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
            return row

        schemas = SCHEMAS_CUSTOM["report_adapters_missing"]
        field = schemas["adapters_missing"]["name_qual"]

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

        row[field] = missing
        return row

    def is_excluded(self, schema):
        """Check if a name supplied to field_excludes matches one of GET_SCHEMA_KEYS."""
        excludes = listify(self.GETARGS.get("field_excludes", []))
        for exclude in excludes:
            for key in GET_SCHEMA_KEYS:
                if schema.get(key, None) == exclude:
                    return True
        return False

    def filter_schemas(self, schemas):
        """Pass."""
        return [x for x in schemas if not self.is_excluded(schema=x)]

    def filter_sub_schemas(self, schema):
        """Pass."""
        schemas = schema["sub_fields"]
        schemas = self.filter_schemas(schemas=schemas)
        schemas = [x for x in schemas if x["is_root"]]
        return schemas

    def tags_add(self, row):
        """Pass."""
        tags = listify(self.GETARGS.get("tags_add", []))
        if not tags:
            return row

        tag_row = {"internal_axon_id": row["internal_axon_id"]}

        if tag_row not in self.TAG_ROWS_ADD:
            self.TAG_ROWS_ADD.append(tag_row)
        return row

    def tags_remove(self, row):
        """Pass."""
        tags = listify(self.GETARGS.get("tags_remove", []))
        if not tags:
            return row

        tag_row = {"internal_axon_id": row["internal_axon_id"]}

        if tag_row not in self.TAG_ROWS_REMOVE:
            self.TAG_ROWS_REMOVE.append(tag_row)

        return row

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
        self.echo(msg=f"Exporting to stdout")
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
