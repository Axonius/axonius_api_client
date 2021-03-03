# -*- coding: utf-8 -*-
"""Base callbacks."""
import copy
import logging
import re
import sys
from typing import Generator, List, Optional, Tuple, Union

from ... import DEFAULT_PATH
from ...constants.api import FIELD_JOINER, FIELD_TRIM_LEN, FIELD_TRIM_STR
from ...constants.fields import AGG_ADAPTER_NAME, SCHEMAS_CUSTOM
from ...exceptions import ApiError
from ...parsers.fields import schema_custom
from ...tools import (
    calc_percent,
    coerce_int,
    echo_error,
    echo_ok,
    echo_warn,
    get_path,
    join_kv,
    listify,
    longest_str,
    strip_right,
)


class Base:
    """Callbacks for formatting asset data.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

        * :meth:`args_map` for callback generic arguments to format assets.
        * :meth:`args_map_custom` for callback specific arguments to format and export data.

    """

    @classmethod
    def args_map(cls) -> dict:
        """Get all of the argument names and their defaults for this callbacks object.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is either ``client.devices`` or ``client.users``

            >>> apiobj = client.devices  # or client.users

            Flatten complex fields -  Will take all sub fields of complex fields and put them
            on the root level with their values index correlated to each other.

            >>> assets = apiobj.get(fields=["network_interfaces"], field_flatten=True)

            Explode a single field - will take that field and create new rows for list item.

            >>> assets = apiobj.get(field_explode="hostname")

            Exclude fields - Will remove fields from the final output.

            >>> assets = apiobj.get(field_excludes=["internal_axon_id", "adapter_list_length"])

            Use field titles - Will change internal field names to their titles.

            >>> assets = apiobj.get(field_titles=True)

            Join fields - Will join multi value fields with carriage returns.

            >>> assets = apiobj.get(field_join=True)

            Join fields with no trim and custom join value - Will join multi value fields
            with ``;;`` and do not trim the joined value to excels maximum cell length.

            >>> assets = apiobj.get(field_join=True, field_join_value=";;", field_join_trim=0)

            Add fields as empty values for fields that did not return.

            >>> assets = apiobj.get(field_null=True)

            Add fields as empty values for fields that did not return with a custom null value.

            >>> assets = apiobj.get(
            ...     field_null=True,
            ...     field_null_value="EMPTY",
            ...     field_null_value_complex="EMPTY LIST",
            ... )

            Add and remove tags to all assets returned.

            >>> assets = apiobj.get(tags_add=["tag1", "tag2"], tags_remove=["tag3", "tag4"])

            Generate a report of adapters that are missing from each asset.

            >>> assets = apiobj.get(report_adapters_missing=True)

            Generate a report of installed software that does not match a list of regex for each
            asset.

            >>> assets = apiobj.get(report_software_whitelist=["chrome", "^adobe.*acrobat"])

            Echo to STDERR progress messages.

            >>> assets = apiobj.get(do_echo=True)

            Change the amount of assets that echo page progress if do_echo is true.

            >>> assets = apiobj.get(do_echo=True, page_progress=100)

            Supply a set of custom callbacks to process each row before all builtin callbacks
            are run. Custom callbacks receive two arguments: ``self`` (the current callback object)
            and ``rows`` (the current rows being processed). Custom callbacks must return a list of
            rows.

            >>> def custom_cb1(self, rows):
            ...     for row in rows:
            ...         row["internal_axon_id"] = row["internal_axon_id"].upper()
            ...     return rows
            ...
            >>> assets = apiobj.get(custom_cbs=[custom_cb1])

        See Also:
            * :meth:`args_map_custom` for callback specific arguments to format and export data.

        Notes:
            These arguments can be supplied as extra kwargs passed to
            :meth:`axonius_api_client.api.assets.users.Users.get` or
            :meth:`axonius_api_client.api.assets.devices.Devices.get`

        """
        args = {}
        args.update(cls.args_map_base())
        args.update(cls.args_map_custom())
        return args

    @classmethod
    def args_map_custom(cls) -> dict:
        """Get the custom argument names and their defaults for this callbacks object.

        See Also:
            :meth:`args_map` for the arguments for all callback objects.

        Notes:
            This callback object has no custom arguments.
        """
        return {}

    @classmethod
    def args_map_base(cls) -> dict:
        """Get the map of arguments that can be supplied to GETARGS."""
        return {
            "field_excludes": [],
            "field_flatten": False,
            "field_explode": None,
            "field_titles": False,
            "field_compress": False,
            "field_replace": [],
            "field_join": False,
            "field_join_value": FIELD_JOINER,
            "field_join_trim": FIELD_TRIM_LEN,
            "field_null": False,
            "field_null_value": None,
            "field_null_value_complex": [],
            "tags_add": [],
            "tags_remove": [],
            "report_adapters_missing": False,
            "report_software_whitelist": [],
            "page_progress": 10000,
            "do_echo": False,
            "custom_cbs": [],
        }

    def get_arg_value(self, arg: str) -> Union[str, list, bool, int]:
        """Get an argument value.

        Args:
            arg: key to get from :attr:`GETARGS` with a default value from :meth:`args_map`
        """
        return self.GETARGS.get(arg, self.args_map()[arg])

    def set_arg_value(self, arg: str, value: Union[str, list, bool, int]):
        """Set an argument value.

        Args:
            arg: key to set in :attr:`GETARGS`
            value: value to set for key
        """
        self.GETARGS[arg] = value

    def __init__(
        self,
        apiobj,
        store: dict,
        state: Optional[dict] = None,
        getargs: dict = None,
    ):
        """Callbacks base class for assets.

        Args:
            apiobj (:obj:`axonius_api_client.api.assets.asset_mixin.AssetMixin`): Asset object
                that created this callback
            store: store tracker of assets get method that created this callback
            state: state tracker of assets get method that created this callback
            getargs: kwargs passed to assets get method that created this callback
        """
        self.LOG: logging.Logger = apiobj.LOG.getChild(self.__class__.__name__)
        """logger for this object."""

        self.APIOBJ = apiobj
        self.ALL_SCHEMAS: dict = apiobj.fields.get()
        self.STATE: dict = state or {}
        self.STORE: dict = store or {}
        self.CURRENT_ROWS: List[dict] = []
        self.GETARGS: dict = getargs or {}
        self.TAG_ROWS_ADD: List[dict] = []
        self.TAG_ROWS_REMOVE: List[dict] = []
        self.CUSTOM_CB_EXC: List[dict] = []
        self._init()

    def _init(self):
        """Post init setup."""
        pass

    def start(self, **kwargs):
        """Start this callbacks object."""
        join = "\n   - "
        self.echo(msg=f"Starting {self}")

        cbargs = join + join.join(join_kv(obj=self.GETARGS))
        self.LOG.debug(f"Get Extra Arguments: {cbargs}")

        config = join + join.join(self.args_strs)
        self.echo(msg=f"Configuration: {config}")

        store = join + join.join(join_kv(obj=self.STORE))
        self.echo(msg=f"Get Arguments: {store}")

    def echo_columns(self, **kwargs):
        """Echo the columns of the fields selected."""
        if getattr(self, "ECHO_DONE", False):
            return

        join = "\n   - "
        schemas_pretty = self.APIOBJ.fields._prettify_schemas(schemas=self.schemas_selected)
        schemas_pretty = join + join.join(schemas_pretty)
        self.echo(msg=f"Selected Columns: {schemas_pretty}")

        if self.excluded_schemas:
            schemas_pretty = self.APIOBJ.fields._prettify_schemas(schemas=self.excluded_schemas)
            schemas_pretty = join + join.join(schemas_pretty)
            self.echo(msg=f"Excluded Columns: {schemas_pretty}")

        final_columns = join + join.join(self.final_columns)
        self.echo(msg=f"Final Columns: {final_columns}")
        self.ECHO_DONE = True

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        self.do_tagging()
        self.echo(msg=f"Stopping {self}")

    def echo_page_progress(self):
        """Echo progress per N rows using an echo method."""
        page_progress = self.get_arg_value("page_progress")
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

    def do_pre_row(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Pre-processing callbacks for current row.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        self.CURRENT_ROWS = rows
        self.STATE.setdefault("rows_processed_total", 0)
        self.STATE["rows_processed_total"] += 1
        self.echo_columns()
        self.echo_page_progress()
        return rows

    def process_row(self, row: Union[List[dict], dict]) -> List[dict]:
        """Process the callbacks for current row.

        Args:
            row: row to process
        """
        rows = listify(row)
        rows = self.do_pre_row(rows=rows)
        rows = self.do_row(rows=rows)
        return rows

    @property
    def callbacks(self) -> list:
        """Get order of callbacks to run."""
        return [
            self.do_custom_cbs,
            self.process_tags_to_add,
            self.process_tags_to_remove,
            self.add_report_adapters_missing,
            self.add_report_software_whitelist,
            self.do_excludes,
            self.do_add_null_values,
            self.do_flatten_fields,
            self.do_explode_field,
            self.do_join_values,
            self.do_change_field_titles,
            self.do_change_field_compress,
            self.do_change_field_replace,
        ]

    def do_row(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Execute the callbacks for current row.

        Args:
            rows: rows to process
        """
        for cb in self.callbacks:
            rows = cb(rows=rows)
        return rows

    def do_custom_cbs(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Execute any custom callbacks for current row.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        custom_cbs = listify(self.get_arg_value("custom_cbs"))

        for custom_cb in custom_cbs:
            try:
                rows = custom_cb(self=self, rows=rows)
                rows = listify(rows)
            except Exception as exc:
                msg = f"Custom callback {custom_cb} failed: {exc}"
                self.CUSTOM_CB_EXC.append({"cb": custom_cb, "exc": exc, "msg": msg})
                self.echo(msg=msg, error="exception", abort=False)
        return rows

    def do_add_null_values(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Null out missing fields.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        if not self.get_arg_value("field_null"):
            return rows

        for row in rows:
            for schema in self.schemas_selected:
                self._do_add_null_values(row=row, schema=schema)
        return rows

    def _do_add_null_values(self, row: dict, schema: dict, key: str = "name_qual"):
        """Null out missing fields.

        Args:
            row: row being processed
            schema: field schema to add null values for
            key: key of field schema to add null value for in row
        """
        if self.is_excluded(schema=schema):
            return row

        null_value = self.get_arg_value("field_null_value")
        complex_null_value = self.get_arg_value("field_null_value_complex")

        field = schema[key]

        if schema["is_complex"]:

            row[field] = listify(row.get(field, complex_null_value))

            for item in row[field]:
                for sub_schema in self.get_sub_schemas(schema=schema):
                    self._do_add_null_values(schema=sub_schema, row=item, key="name")
        else:
            row[field] = row.get(field, null_value)

    def do_excludes(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Asset callback to remove fields from row.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        if not self.get_arg_value("field_excludes"):
            return rows

        for row in rows:
            self._do_excludes(row=row)
        return rows

    def _do_excludes(self, row: dict):
        """Asset callback to remove fields from row.

        Args:
            row: row being processed
        """
        for schema in self.schemas_selected:
            if self.is_excluded(schema=schema):
                row.pop(schema["name_qual"], None)
                continue

            if schema["is_complex"]:
                items = listify(row.get(schema["name_qual"], []))
                for sub_schema in schema["sub_fields"]:
                    if self.is_excluded(schema=sub_schema):
                        for item in items:
                            item.pop(sub_schema["name"], None)

    def do_join_values(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Join values.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        if not self.get_arg_value("field_join"):
            return rows

        for row in rows:
            self._do_join_values(row=row)
        return rows

    def _do_join_values(self, row: dict):
        """Join values.

        Args:
            row: row being processed
        """
        joiner = str(self.get_arg_value("field_join_value"))
        trim_len = coerce_int(self.get_arg_value("field_join_trim"))
        trim_str = FIELD_TRIM_STR

        for field in row:
            if isinstance(row[field], list):
                row[field] = joiner.join([str(x) for x in row[field]])

            if trim_len and isinstance(row[field], str) and len(row[field]) >= trim_len:
                field_len = len(row[field])
                msg = trim_str.format(field_len=field_len, trim_len=trim_len)
                row[field] = joiner.join([row[field][:trim_len], msg])

    def do_change_field_replace(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Asset callback to replace characters.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        if not self.field_replacements:
            return rows

        rows = [{self._field_replace(key=k): v for k, v in row.items()} for row in rows]
        return rows

    def _field_replace(self, key: str) -> str:
        """Parse fields into required format."""
        if self.field_replacements:
            for x, y in self.field_replacements:
                key = key.replace(x, y)
        return key

    @property
    def field_replacements(self) -> List[Tuple[str, str]]:
        """Parse the supplied list of field name replacements."""

        def parse_replace(replace):
            if isinstance(replace, str):
                replace = replace.split("=", maxsplit=1)

            if not isinstance(replace, (tuple, list)) or not replace[0]:
                replace = []

            if len(replace) == 1:
                replace = [replace[0], ""]

            return replace

        if not hasattr(self, "_field_replacements"):
            replaces = listify(self.get_arg_value("field_replace"))
            replaces = [parse_replace(x) for x in replaces]
            self._field_replacements = [x for x in replaces if x]
        return self._field_replacements

    def do_change_field_compress(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Asset callback to shorten field names.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        if not self.get_arg_value("field_compress"):
            return rows
        rows = [{self._field_compress(key=k): v for k, v in row.items()} for row in rows]
        return rows

    def _field_compress(self, key: str) -> str:
        """Parse fields into required format."""
        if not self.get_arg_value("field_compress"):
            return key

        splits = key.split(".")
        prefix = ""

        if splits[0] == "specific_data":
            prefix = AGG_ADAPTER_NAME
            # remove 'specific_data.data'
            splits = splits[2:]
        elif splits[0] == "adapters_data":
            prefix = strip_right(obj=splits[1], fix="_adapter")
            # remove 'adapters_data.aws_adapter'
            splits = splits[2:]
        else:
            return key

        new_key = ".".join(splits)
        return ":".join([x for x in [prefix, new_key] if x])

    def do_change_field_titles(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Asset callback to change qual name to title.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        if not self.get_arg_value("field_titles"):
            return rows

        for row in rows:
            self._do_change_field_titles(row=row)
        return rows

    def _do_change_field_titles(self, row: dict):
        """Asset callback to change qual name to title.

        Args:
            row: row being processed
        """
        null_value = self.get_arg_value("field_null_value")

        for schema in self.final_schemas:
            title = schema["column_title"]
            name = schema["name_qual"]
            is_complex = schema["is_complex"]
            default = [] if is_complex else null_value
            row[title] = row.pop(name, default)

    def do_flatten_fields(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Asset callback to flatten complex fields.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        if not self.get_arg_value("field_flatten"):
            return rows

        for row in rows:
            for schema in self.schemas_selected:
                if self.schema_to_explode != schema:
                    self._do_flatten_fields(row=row, schema=schema)

        return rows

    def _do_flatten_fields(self, row: dict, schema: dict):
        """Asset callback to flatten complex fields.

        Args:
            row: row being processed
        """
        if self.is_excluded(schema=schema):
            return

        if not schema["is_complex"]:
            return

        null_value = self.get_arg_value("field_null_value")

        items = listify(row.pop(schema["name_qual"], []))

        for sub_schema in self.get_sub_schemas(schema=schema):
            row[sub_schema["name_qual"]] = []
            # TBD: handle complex sub-fields

            for item in items:
                value = item.pop(sub_schema["name"], null_value)
                value = value if isinstance(value, list) else [value]
                row[sub_schema["name_qual"]] += value

    def do_explode_field(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Explode a field into multiple rows.

        Args:
            row: row being processed
        """
        rows = listify(rows)
        explode = self.get_arg_value("field_explode")

        if not explode or self.is_excluded(schema=self.schema_to_explode):
            return rows

        new_rows = []
        for row in rows:
            new_rows += self._do_explode_field(row=row)
        return new_rows

    def _do_explode_field(self, row: dict) -> List[dict]:
        """Explode a field into multiple rows.

        Args:
            row: row being processed
        """
        null_value = self.get_arg_value("field_null_value")

        schema = self.schema_to_explode
        field = schema["name_qual"]

        if len(listify(row.get(field, []))) <= 1:
            self._do_flatten_fields(row=row, schema=schema)
            return [row]

        items = listify(row.pop(field, []))
        new_rows_map = {}

        if schema["is_complex"]:
            for sub_schema in self.get_sub_schemas(schema=schema):
                for idx, item in enumerate(items):
                    new_rows_map.setdefault(idx, copy.deepcopy(row))
                    value = item.pop(sub_schema["name"], null_value)
                    new_rows_map[idx][sub_schema["name_qual"]] = value
        else:
            for idx, item in enumerate(items):
                new_rows_map.setdefault(idx, copy.deepcopy(row))
                new_rows_map[idx][schema["name_qual"]] = item

        return [new_rows_map[idx] for idx in new_rows_map]

    def do_tagging(self):
        """Add or remove tags to assets."""
        self.do_tag_add()
        self.do_tag_remove()

    def do_tag_add(self):
        """Add tags to assets."""
        tags_add = listify(self.get_arg_value("tags_add"))
        rows_add = self.TAG_ROWS_ADD
        if tags_add and rows_add:
            self.echo(msg=f"Adding tags {tags_add} to {len(rows_add)} assets")
            self.APIOBJ.labels.add(rows=rows_add, labels=tags_add)

    def do_tag_remove(self):
        """Remove tags from assets."""
        tags_remove = listify(self.get_arg_value("tags_remove"))
        rows_remove = self.TAG_ROWS_REMOVE
        if tags_remove and rows_remove:
            self.echo(msg=f"Removing tags {tags_remove} from {len(rows_remove)} assets")
            self.APIOBJ.labels.remove(rows=rows_remove, labels=tags_remove)

    def process_tags_to_add(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Add assets to tracker for adding tags.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        tags = listify(self.get_arg_value("tags_add"))
        if not tags:
            return rows

        for row in rows:
            tag_row = {"internal_axon_id": row["internal_axon_id"]}

            if tag_row not in self.TAG_ROWS_ADD:
                self.TAG_ROWS_ADD.append(tag_row)
        return rows

    def process_tags_to_remove(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Add assets to tracker for removing tags.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        tags = listify(self.get_arg_value("tags_remove"))
        if not tags:
            return rows

        for row in rows:
            tag_row = {"internal_axon_id": row["internal_axon_id"]}

            if tag_row not in self.TAG_ROWS_REMOVE:
                self.TAG_ROWS_REMOVE.append(tag_row)

        return rows

    def add_report_software_whitelist(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Process report: Software whitelist.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        whitelists = listify(self.get_arg_value("report_software_whitelist"))

        if not whitelists:
            return rows

        for row in rows:
            self._add_report_software_whitelist(row=row)
        return rows

    def _add_report_software_whitelist(self, row: dict):
        """Process report: Software whitelist.

        Args:
            row: row being processed
        """
        whitelists = listify(self.get_arg_value("report_software_whitelist"))

        sw_field = "specific_data.data.installed_software"

        if sw_field not in self.fields_selected:
            msg = f"Must include field (column) {sw_field!r}"
            self.echo(msg=msg, error=ApiError, level="error")

        sws = listify(row.get(sw_field, []))
        names = [x.get("name") for x in sws if x.get("name") and isinstance(x.get("name"), str)]

        extras = [n for n in names if any([re.search(x, n, re.I)] for x in whitelists)]
        missing = [x for x in whitelists if any([re.search(x, n, re.I) for n in names])]

        schemas = SCHEMAS_CUSTOM["report_software_whitelist"]
        row[schemas["software_missing"]["name_qual"]] = sorted(list(set(missing)))
        row[schemas["software_whitelist"]["name_qual"]] = whitelists
        row[schemas["software_extra"]["name_qual"]] = sorted(list(set(extras)))

    def add_report_adapters_missing(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Process report: Missing adapters.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        missing = self.get_arg_value("report_adapters_missing")
        if not missing:
            return rows

        for row in rows:
            self._add_report_adapters_missing(row=row)
        return rows

    def _add_report_adapters_missing(self, row: dict):
        """Process report: Missing adapters.

        Args:
            row: row being processed
        """
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

    # TBD: make this support normal field selection concepts
    def is_excluded(self, schema: dict) -> bool:
        """Check if a name supplied to field_excludes matches one of FIND_KEYS.

        Args:
            schema: field schema
        """
        for excluded_schema in self.excluded_schemas:
            for key in self.FIND_KEYS:
                schema_key = schema.get(key, None)
                excluded_key = excluded_schema.get(key, None)
                if (schema_key and excluded_schema) and (schema_key == excluded_key):
                    return True
        return False

    @property
    def excluded_schemas(self) -> List[dict]:
        """List of all schemas that should be excluded."""
        if not hasattr(self, "_excluded_schemas"):
            excludes = listify(self.get_arg_value("field_excludes"))
            self._excluded_schemas = self.APIOBJ.fields.get_field_names_eq(value=excludes, key=None)
        return self._excluded_schemas

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
        """Echo a message to console or log it.

        Args:
            msg: message to echo
            error: message is an error
            warning: message is a warning
            level: logging level for non error/non warning messages
            level_error: logging level for error messages
            level_warning: logging level for warning messages
            abort: sys.exit(1) if error is true
        """
        do_echo = self.get_arg_value("do_echo")

        if do_echo:
            if warning:
                echo_warn(msg=msg)  # pragma: no cover
            elif error:
                echo_error(msg=msg, abort=abort)
            else:
                echo_ok(msg=msg)
            return

        if warning:
            getattr(self.LOG, level_warning)(msg)  # pragma: no cover
        elif error:
            getattr(self.LOG, level_error)(msg)
            if abort:
                raise error(msg)
        else:
            getattr(self.LOG, level)(msg)

    def get_sub_schemas(self, schema: dict) -> Generator[dict, None, None]:
        """Get all the schemas of sub fields for a complex field.

        Args:
            schema: schema of complex field
        """
        sub_schemas = listify(schema.get("sub_fields"))
        for sub_schema in sub_schemas:
            if self.is_excluded(schema=sub_schema) or not sub_schema["is_root"]:
                continue
            yield sub_schema

    @property
    def custom_schemas(self) -> List[dict]:
        """Get the custom schemas based on GETARGS."""
        schemas = []
        if self.get_arg_value("report_adapters_missing"):
            schemas += list(SCHEMAS_CUSTOM["report_adapters_missing"].values())
        if self.get_arg_value("report_software_whitelist"):
            schemas += list(SCHEMAS_CUSTOM["report_software_whitelist"].values())
        return schemas

    @property
    def final_schemas(self) -> List[dict]:
        """Get the schemas that will be returned."""
        if hasattr(self, "_final_schemas"):
            return self._final_schemas

        flat = self.get_arg_value("field_flatten")
        explode_field = self.schema_to_explode.get("name_qual", "")

        final = {}

        for schema in self.schemas_selected:
            if self.is_excluded(schema=schema):
                continue
            name = schema["name_qual"]
            is_explode_field = name == explode_field
            if schema["is_complex"] and (is_explode_field or flat):
                for sub_schema in self.get_sub_schemas(schema=schema):
                    final[sub_schema["name_qual"]] = sub_schema
            else:
                final.setdefault(name, schema)

        self._final_schemas = list(final.values())
        return self._final_schemas

    @property
    def final_columns(self) -> List[str]:
        """Get the columns that will be returned."""

        def get_key(s):
            return self._field_replace(self._field_compress(s[key]))

        if hasattr(self, "_final_columns"):
            return self._final_columns

        use_titles = self.get_arg_value("field_titles")
        key = "column_title" if use_titles else "name_qual"
        self._final_columns = [get_key(s) for s in self.final_schemas]
        return self._final_columns

    @property
    def fields_selected(self) -> List[str]:
        """Get the names of the fields that were selected."""
        if hasattr(self, "_fields_selected"):
            return self._fields_selected

        include_details = self.STORE.get("include_details", False)

        fields = listify(self.STORE.get("fields", []))
        api_fields = [x for x in self.APIOBJ.FIELDS_API if x not in fields]

        if include_details:  # pragma: no cover
            api_fields += ["meta_data.client_used", "unique_adapter_names_details"]

        self._fields_selected = []

        for field in api_fields + fields:
            self._fields_selected.append(field)
            if include_details:
                field_details = f"{field}_details"
                self._fields_selected.append(field_details)

        for row in self.CURRENT_ROWS:
            self._fields_selected += [x for x in row if x not in self._fields_selected]

        return self._fields_selected

    @property
    def schemas_selected(self) -> List[dict]:
        """Get the schemas of the fields that were selected."""
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
            else:  # pragma: no cover
                self._schemas_selected.append(schema_custom(name=field))
                msg = f"No schema found for field {field}"
                self.echo(msg=msg, warning=True)

        return self._schemas_selected

    @property
    def schema_to_explode(self) -> dict:
        """Get the schema of the field that should be exploded."""
        if hasattr(self, "_schema_to_explode"):
            return self._schema_to_explode

        explode = self.get_arg_value("field_explode")

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
        """Build a map of adapters that have connections."""
        if getattr(self, "_adapter_map", None):
            return self._adapter_map

        self._adapters_meta = getattr(
            self, "_adapters_meta", self.APIOBJ.adapters.get(get_clients=False)
        )

        self._adapter_map = {}
        self._adapter_map["has_cnx"] = has_cnx = []
        self._adapter_map["all"] = all_adapters = []
        self._adapter_map["all_fields"] = [f"{x}_adapter" for x in self.ALL_SCHEMAS]

        for adapter in self._adapters_meta:
            name_raw = adapter["name_raw"]
            cnt = adapter["cnx_count_total"]

            if name_raw not in all_adapters:
                all_adapters.append(name_raw)

            if cnt and name_raw not in has_cnx:
                has_cnx.append(name_raw)

        # self._adapter_map = {k: list(v) for k, v in self._adapter_map.items()}
        return self._adapter_map

    @property
    def args_strs(self) -> List[str]:
        """Get a list of strings that describe each arg in :meth:`args_map`."""
        lines = []
        arg_desc = {k: v for k, v in ARG_DESCRIPTIONS.items() if k in self.args_map()}
        longest = longest_str(list(arg_desc.values()))
        for arg in self.args_map():
            desc = f"{arg_desc[arg]}:"
            value = self.get_arg_value(arg)

            if isinstance(value, str):
                value = repr(value)

            lines.append(f"{desc:{longest}}{value}")
        return lines

    def __str__(self) -> str:
        """Show info for this object."""
        return f"{self.CB_NAME.upper()} processor"

    def __repr__(self) -> str:
        """Show info for this object."""
        return self.__str__()

    CB_NAME: str = "base"
    """name for this callback"""

    FIND_KEYS: List[str] = ["name", "name_qual", "column_title", "name_base"]
    """field schema keys to use when finding a fields schema"""

    APIOBJ = None
    """:obj:`axonius_api_client.api.assets.asset_mixin.AssetMixin`: assets object."""

    ALL_SCHEMAS: dict = None
    """Map of adapter -> field schemas."""

    STATE: dict = None
    """state dict used by get assets method to track paging."""

    STORE: dict = None
    """store dict used by get assets method to track arguments."""

    CURRENT_ROWS: None
    """current rows being processed"""

    GETARGS: dict = None
    """original kwargs supplied to get assets method."""

    TAG_ROWS_ADD: List[dict] = None
    """tracker of assets to add tags to in :meth:`do_tagging`."""

    TAG_ROWS_REMOVE: List[dict] = None
    """tracker of assets to remove tags from in :meth:`do_tagging`."""

    CUSTOM_CB_EXC: List[dict] = None
    """tracker of custom callbacks that have been executed by :meth:`do_custom_cbs`"""


class ExportMixins(Base):
    """Export mixins for callbacks."""

    @classmethod
    def args_map_export(cls) -> dict:
        """Get the export argument names and their defaults for this callbacks object.

        See Also:
            :meth:`args_map_custom` for the arguments specific to this callback object.

            :meth:`args_map` for the arguments for all callback objects.

        """
        return {
            "export_file": None,
            "export_path": DEFAULT_PATH,
            "export_overwrite": False,
            "export_schema": False,
            "export_fd": None,
            "export_fd_close": True,
        }

    def open_fd_arg(self):
        """Open a file descriptor supplied in GETARGS."""
        self._fd = self.get_arg_value("export_fd")
        self._fd_close = self.get_arg_value("export_fd_close")
        self.echo(msg=f"Exporting to {self._fd}")
        return self._fd

    def open_fd_path(self):
        """Open a file descriptor for a path."""
        self._export_file = self.get_arg_value("export_file")
        self._export_path = self.get_arg_value("export_path")
        self._export_overwrite = self.get_arg_value("export_overwrite")

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
        self._fd_close = self.get_arg_value("export_fd_close")
        self._fd = self._file_path.open(mode="w", encoding="utf-8")
        self.echo(msg=f"Exporting to file '{fp}' ({mode})")
        return self._fd

    def open_fd_stdout(self):
        """Open a file descriptor to STDOUT."""
        self._file_path = None
        self._fd_close = False
        self._fd = sys.stdout
        self.echo(msg="Exporting to stdout")
        return self._fd

    def open_fd(self):
        """Open a file descriptor."""
        if self.get_arg_value("export_fd"):
            self.open_fd_arg()
        elif self.get_arg_value("export_file"):
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


ARG_DESCRIPTIONS: dict = {
    "field_excludes": "Exclude fields",
    "field_flatten": "Flatten complex fields",
    "field_explode": "Explode field",
    "field_titles": "Rename fields to titles",
    "field_compress": "Shorten field names",
    "field_replace": "Replace characters in field names",
    "field_join": "Join field values",
    "field_join_value": "Join field values using",
    "field_join_trim": "Join field character limit",
    "field_null": "Add missing fields",
    "field_null_value": "Missing field value",
    "field_null_value_complex": "Missing complex field value",
    "tags_add": "Add tags",
    "tags_remove": "Remove tags",
    "report_adapters_missing": "Report Missing Adapters",
    "report_software_whitelist": "Report Missing Software",
    "page_progress": "Echo page progress every N assets",
    "do_echo": "Echo messages to console",
    "custom_cbs": "Custom callbacks to perform on assets",
    "json_flat": "Produce flat JSON",
    "csv_key_miss": "Value to use when CSV keys are missing",
    "csv_key_extras": "What to do with extra CSV columns",
    "csv_dialect": "Dialect to export CSV as",
    "csv_quoting": "What quoting to use in CSV export",
    "export_file": "Export to file",
    "export_path": "Export file to path",
    "export_overwrite": "Export overwrite file",
    "export_schema": "Export schema of fields",
    "export_fd": "Export to a file descriptor",
    "export_fd_close": "Close the file descriptor when done",
    "table_format": "Use table format",
    "table_max_rows": "Maximum table rows",
    "table_api_fields": "Include API fields",
    "xlsx_column_length": "Length to use for every column",
    "xlsx_cell_format": "Formatting to apply to every cell",
}
"""Descriptions of all arguments for all callbacks"""
