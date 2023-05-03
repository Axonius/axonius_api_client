# -*- coding: utf-8 -*-
"""Base callbacks."""
import logging
import pathlib
import re
import sys
import typing as t
from typing import IO, Generator, List, Optional, Tuple, Union

from ... import DEFAULT_PATH
from ...constants.api import FIELD_JOINER, FIELD_TRIM_LEN, FIELD_TRIM_STR
from ...constants.fields import (
    AGG_ADAPTER_NAME,
    FIELDS_DETAILS,
    FIELDS_DETAILS_EXCLUDE,
    FIELDS_ENTITY_PASSTHRU,
    SCHEMAS_CUSTOM,
)
from ...exceptions import ApiError
from ...tools import (
    PathLike,
    calc_percent,
    check_path_is_not_dir,
    coerce_int,
    dt_now,
    echo_debug,
    echo_error,
    echo_ok,
    echo_warn,
    get_path,
    get_paths_format,
    is_subclass_safe,
    join_kv,
    listify,
    longest_str,
    path_backup_file,
    strip_right,
)


# noinspection SpellCheckingInspection
def crjoin(value):
    """Pass."""
    joiner = "\n   - "
    return joiner + joiner.join(value)


# noinspection PyProtectedMember,PyAttributeOutsideInit
class Base:
    """Callbacks for formatting asset data.

    Examples:
        * :meth:`args_map` for callback generic arguments to format assets.
        * :meth:`args_map_custom` for callback specific arguments to format and export data.

    """

    @classmethod
    def args_map(cls) -> dict:
        """Get all the argument names and their defaults for this callbacks object.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is either ``client.devices`` or ``client.users``

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities

            Flatten complex fields -  Will take all sub-fields of complex fields and put them
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

            Change the amount of assets that echo page progress when do_echo is true.

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
            "tags_add_invert_selection": False,
            "tags_remove": [],
            "tags_remove_invert_selection": False,
            "report_adapters_missing": False,
            "report_software_whitelist": [],
            "page_progress": 10000,
            "do_echo": False,
            "custom_cbs": [],
            "debug_timing": False,
            "explode_entities": False,
            "include_dates": False,
            "csv_field_flatten": True,
            "csv_field_join": True,
            "csv_field_null": True,
        }

    def get_arg_value(self, arg: str) -> t.Any:
        """Get an argument value.

        Args:
            arg: key to get from :attr:`GETARGS` with a default value from :meth:`args_map`
        """
        return self.GETARGS.get(arg, self.args_map()[arg])

    def set_arg_value(self, arg: str, value: t.Any):
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
            store: store tracker of get method that created this callback
            state: state tracker of get method that created this callback
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
        self.echo(msg=f"Starting {self}")
        excludes = listify(self.get_arg_value("field_excludes"))
        explode_entities = self.get_arg_value("explode_entities")
        include_details = self.STORE.get("include_details", False)

        if explode_entities:
            if not include_details:
                self.echo(
                    msg=f"Enabling 'include_details' due to 'explode_entities'={explode_entities}",
                    debug=True,
                )
                self.STORE["include_details"] = include_details = True

        if include_details:
            missing = [x for x in FIELDS_DETAILS_EXCLUDE if x not in excludes]
            self.echo(msg=f"Adding fields {missing} to field_excludes: {excludes}", debug=True)
            self.set_arg_value("field_excludes", value=excludes + missing)

        cb_args = crjoin(join_kv(obj=self.GETARGS))
        self.LOG.debug(f"Get Extra Arguments: {cb_args}")

        config = crjoin(self.args_strs)
        self.echo(msg=f"Configuration: {config}")

        store = crjoin(join_kv(obj=self.STORE))
        self.echo(msg=f"Get Arguments: {store}")

    # noinspection PyUnusedLocal
    def echo_columns(self, **kwargs):
        """Echo the columns of the fields selected."""
        if getattr(self, "ECHO_DONE", False):
            return

        schemas_pretty = self.APIOBJ.fields._prettify_schemas(schemas=self.schemas_selected)
        schemas_pretty = crjoin(schemas_pretty)
        self.echo(msg=f"Selected Columns: {schemas_pretty}")

        if self.excluded_schemas:
            schemas_pretty = self.APIOBJ.fields._prettify_schemas(schemas=self.excluded_schemas)
            schemas_pretty = crjoin(schemas_pretty)
            self.echo(msg=f"Excluded Columns: {schemas_pretty}")

        final_columns = crjoin(self.final_columns)
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
            self.add_include_dates,
            self.do_excludes,
            self.do_add_null_values,
            self.do_explode_entities,
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
        debug_timing = self.get_arg_value("debug_timing")

        p_start = None
        cb_start = None
        if debug_timing:  # pragma: no cover
            p_start = dt_now()

        for cb in self.callbacks:
            if debug_timing:  # pragma: no cover
                cb_start = dt_now()

            rows = cb(rows=rows)
            # print(f"{cb} {json_dump(rows)}")
            if debug_timing and cb_start:  # pragma: no cover
                cb_delta = dt_now() - cb_start
                self.LOG.debug(f"CALLBACK {cb} took {cb_delta} for {len(rows)} rows")

        if debug_timing and p_start:  # pragma: no cover
            p_delta = dt_now() - p_start
            self.LOG.debug(f"CALLBACKS TOOK {p_delta} for {len(rows)} rows")

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
        field_null = self.get_arg_value("field_null")
        if not field_null:
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
        if self.is_excluded(schema=schema) or schema.get("is_details", False):
            return row

        null_value = self.get_arg_value("field_null_value")
        complex_null_value = self.get_arg_value("field_null_value_complex")

        field = schema[key]

        if schema["is_complex"]:
            if field not in row:
                row[field] = complex_null_value

            for item in row[field]:
                for sub_schema in self.get_sub_schemas(schema=schema):
                    self._do_add_null_values(schema=sub_schema, row=item, key="name")
        else:
            if field not in row:
                row[field] = null_value
        return row

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
            field = schema["name_qual"]
            if self.is_excluded(schema=schema) and field in row:
                row.pop(field)
                continue

            if schema["is_complex"]:
                items = listify(row.get(field, []))
                for sub_schema in schema["sub_fields"]:
                    if self.is_excluded(schema=sub_schema):
                        sub_field = sub_schema["name"]
                        for item in items:
                            if sub_field in item:
                                item.pop(sub_field)

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
            value = row[field]
            if isinstance(value, list):
                row[field] = value = joiner.join([str(x) for x in value])

            if trim_len and isinstance(value, str) and len(value) >= trim_len:
                field_len = len(value)
                msg = trim_str.format(field_len=field_len, trim_len=trim_len)
                value = [value[:trim_len], msg]
                row[field] = joiner.join(value)

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
            """Parse the supplied list of field name replacements."""
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
        complex_null_value = self.get_arg_value("field_null_value_complex")

        for schema in self.final_schemas:
            title = schema["column_title"]
            name = schema["name_qual"]
            is_complex = schema["is_complex"]
            default = complex_null_value if is_complex else null_value
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
                if self.schema_to_explode != schema and not schema.get("is_details", False):
                    self._do_flatten_fields(row=row, schema=schema)

        return rows

    def _do_flatten_fields(self, row: dict, schema: dict):
        """Asset callback to flatten complex fields.

        Args:
            row: row being processed
            schema: schema to use when flattening
        """
        if self.is_excluded(schema=schema):
            return

        if not schema["is_complex"]:
            return

        null_value = self.get_arg_value("field_null_value")
        field = schema["name_qual"]

        # remove the complex field, i.e. specific_data.data.network_interfaces
        # force it into a list of items
        items = listify(row.pop(field, []))

        for sub_schema in self.get_sub_schemas(schema=schema):
            sub_field = sub_schema["name_qual"]
            sub_short = sub_schema["name"]

            # for each sub-field, ensure there is an empty list to store values
            row[sub_field] = []

            # for each complex item, remove the sub-field, force it into a list,
            # and append it to the sub-fields fully qualified name at the root row level
            for item in items:
                value = item.pop(sub_short, null_value)
                value = value if isinstance(value, list) else [value]
                row[sub_field] += value

    def do_explode_entities(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Explode a row into a row for each asset entity.

        Args:
            rows: rows being processed
        """
        rows = listify(rows)
        explode = self.get_arg_value("explode_entities")

        if not explode:
            return rows

        new_rows = []
        for row in rows:
            new_rows += self._do_explode_entities(row=row)
        return new_rows

    def _do_explode_entities(self, row: dict) -> List[dict]:
        """Explode a row into multiple rows for each asset entity.

        Args:
            row: row being processed
        """

        def explode(idx: int, adapter: str) -> dict:
            """Explode a row into a row for each asset entity."""
            new_row = {"adapters": adapter}

            for k, v in row.items():
                if k in FIELDS_ENTITY_PASSTHRU or k.endswith("_preferred"):
                    new_row[k] = v
                    continue

                if (k in FIELDS_DETAILS or k.endswith("_details")) and not k.endswith(
                    "_preferred_details"
                ):
                    new_k = strip_right(obj=k, fix="_details") if k not in FIELDS_DETAILS else k

                    try:
                        new_row.setdefault(new_k, v[idx])
                    except Exception:
                        msg = (
                            f"Adapters length {adapters_cnt} != details length {len(v)} on {k}: {v}"
                        )
                        self.echo(msg=msg, warning=True)
                    continue
            return new_row

        adapters = row.get("adapters") or []
        adapters_cnt = len(adapters)
        new_rows = [explode(idx=idx, adapter=adapter) for idx, adapter in enumerate(adapters)]
        return new_rows

    def do_explode_field(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Explode a field into multiple rows.

        Args:
            rows: rows being processed
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

        if len(listify(row.get(field, []))) <= 1:  # pragma: no cover
            self._do_flatten_fields(row=row, schema=schema)
            return [row]

        items = listify(row.pop(field, []))
        new_rows_map = {}

        for idx, item in enumerate(items):
            new_rows_map[idx] = dict(row)

            if schema["is_complex"]:
                for sub_schema in self.get_sub_schemas(schema=schema):
                    value = item.pop(sub_schema["name"], null_value)
                    new_rows_map[idx][sub_schema["name_qual"]] = value
            else:
                new_rows_map[idx][schema["name_qual"]] = item

        return [new_rows_map[idx] for idx in new_rows_map]

    def do_tagging(self):
        """Add or remove tags to assets."""
        self.do_tag_add()
        self.do_tag_remove()

    def do_tag_add(self):
        """Add tags to assets."""
        tags = listify(self.get_arg_value("tags_add"))
        rows = self.TAG_ROWS_ADD
        invert_selection = self.get_arg_value("tags_add_invert_selection")
        count_tags = len(tags)
        count_supplied = len(rows)
        msgs = [
            f"   Tags supplied ({count_tags}): {tags}",
            f"   Asset IDs supplied ({count_supplied})",
            f"   Invert selection: {invert_selection}",
        ]
        if tags:
            self.echo(["Performing API call to add tags to assets", *msgs])
            count_modified = self.APIOBJ.labels.add(
                rows=rows, labels=tags, invert_selection=invert_selection
            )
            self.echo(msg=[f"API added tags to {count_modified} assets", *msgs])

    def do_tag_remove(self):
        """Remove tags from assets."""
        tags = listify(self.get_arg_value("tags_remove"))
        rows = self.TAG_ROWS_REMOVE
        invert_selection = self.get_arg_value("tags_remove_invert_selection")
        count_tags = len(tags)
        count_supplied = len(rows)
        msgs = [
            f"   Asset IDs supplied ({count_supplied})",
            f"   Tags supplied ({count_tags}): {tags}",
            f"   Invert selection: {invert_selection}",
        ]
        if tags:
            self.echo(["Performing API call to remove tags from assets", *msgs])
            count_modified = self.APIOBJ.labels.remove(
                rows=rows, labels=tags, invert_selection=invert_selection
            )
            msgs = [
                f"API finished removing tags from assets",
                f"   Asset IDs modified: " f"{count_modified}",
                *msgs,
            ]
            self.echo(msg=msgs)

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

    def add_include_dates(self, rows: Union[List[dict], dict]) -> List[dict]:
        """Process report: Add dates (history and current)

        Args:
            rows: rows to process
        """

        def _add_date(row):
            row.update(updater)
            return row

        rows = listify(rows)
        enabled = self.get_arg_value("include_dates")
        if not enabled:
            return rows

        history_date = self.STORE.get("history_date_parsed")
        current_date = str(dt_now())
        schemas = SCHEMAS_CUSTOM["include_dates"]
        updater = {
            schemas["history_date"]["name_qual"]: history_date,
            schemas["current_date"]["name_qual"]: current_date,
        }
        rows = [_add_date(row) for row in rows]
        return rows

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
            self._excluded_schemas = self.APIOBJ.fields.get_field_names_eq(
                value=excludes, key=None, selectable_only=False
            )
        return self._excluded_schemas

    def echo(
        self,
        msg: t.Union[str, t.List[str]],
        debug: bool = False,
        error: Union[bool, str, t.Type[Exception]] = False,
        warning: bool = False,
        level: str = "info",
        level_debug: str = "debug",
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
            level_debug: logging level for debug messages
            level_error: logging level for error messages
            level_warning: logging level for warning messages
            abort: sys.exit(1) if error is true
            debug: message is a debug message
        """
        do_echo = self.get_arg_value("do_echo")
        msg = "\n".join(listify(msg))
        if do_echo:
            if error:
                echo_error(msg=msg, abort=abort)
            elif warning:
                echo_warn(msg=msg)
            elif debug:
                echo_debug(msg=msg)
            else:
                echo_ok(msg=msg)
        else:
            if error:
                getattr(self.LOG, level_error)(msg)
                if abort:
                    if not is_subclass_safe(error, Exception):
                        error = ApiError
                    raise error(msg)
            elif warning:
                getattr(self.LOG, level_warning)(msg)
            elif debug:
                getattr(self.LOG, level_debug)(msg)
            else:
                getattr(self.LOG, level)(msg)

    def get_sub_schemas(self, schema: dict) -> Generator[dict, None, None]:
        """Get all the schemas of sub-fields for a complex field.

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
        if self.get_arg_value("include_dates"):
            schemas += list(SCHEMAS_CUSTOM["include_dates"].values())
        return schemas

    @property
    def final_schemas(self) -> List[dict]:
        """Get the schemas that will be returned."""
        if hasattr(self, "_final_schemas"):
            return self._final_schemas

        flat = self.get_arg_value("field_flatten")
        explode_field = self.schema_to_explode.get("name_qual", "")
        explode_entities = self.get_arg_value("explode_entities")

        final = {}

        for schema in self.schemas_selected:
            if self.is_excluded(schema=schema):
                continue
            name = schema["name_qual"]
            if explode_entities and name.endswith("_details") and name not in FIELDS_DETAILS:
                continue
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
            """Get the key for a schema."""
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

        fields = listify(self.STORE.get("fields_parsed", []))
        api_fields = [x for x in self.APIOBJ.FIELDS_API if x not in fields]

        if include_details:
            api_fields += FIELDS_DETAILS

        self._fields_selected = []

        for field in api_fields + fields:
            self._fields_selected.append(field)
            if include_details and field not in FIELDS_DETAILS and not field.endswith("_details"):
                field_details = f"{field}_details"
                self._fields_selected.append(field_details)

        for row in self.CURRENT_ROWS:
            self._fields_selected += [x for x in row if x not in self._fields_selected]

        return self._fields_selected

        # TBD move _details fields from selected to final?!

    @property
    def schemas_selected(self) -> List[dict]:
        """Get the schemas of the fields that were selected."""
        if hasattr(self, "_schemas_selected"):
            return self._schemas_selected

        self._schemas_selected = self.custom_schemas + self.APIOBJ.fields.get_field_names_eq(
            value=self.fields_selected, key=None, fields_error=False, selectable_only=False
        )
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
        self.echo(msg=f"Explode field {explode!r} not found, valid fields:{valids}", error=ApiError)

    @property
    def adapter_map(self) -> dict:
        """Build a map of adapters that have connections."""
        if getattr(self, "_adapter_map", None):
            return getattr(self, "_adapter_map", None)

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

    FIND_KEYS: List[str] = ["name", "name_qual", "column_title"]
    """field schema keys to use when finding a fields schema"""

    APIOBJ = None
    """:obj:`axonius_api_client.api.assets.asset_mixin.AssetMixin`: assets object."""

    ALL_SCHEMAS: dict = None
    """Map of adapter -> field schemas."""

    STATE: dict = None
    """state dict used by get assets method to track paging."""

    STORE: dict = None
    """store dict used by get assets method to track arguments."""

    CURRENT_ROWS: t.Optional[t.List[dict]] = None
    """current rows being processed"""

    GETARGS: dict = None
    """original kwargs supplied to get assets method."""

    TAG_ROWS_ADD: List[dict] = None
    """tracker of assets to add tags to in :meth:`do_tagging`."""

    TAG_ROWS_REMOVE: List[dict] = None
    """tracker of assets to remove tags from in :meth:`do_tagging`."""

    CUSTOM_CB_EXC: List[dict] = None
    """tracker of custom callbacks that have been executed by :meth:`do_custom_cbs`"""


# noinspection PyAttributeOutsideInit
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
            "export_backup": False,
            "export_schema": False,
            "export_fd": None,
            "export_fd_close": True,
        }

    def open_fd(self) -> IO:
        """Open a file descriptor."""
        if self.arg_export_fd:
            return self.open_fd_arg()
        elif self.arg_export_file:
            return self.open_fd_path()
        else:
            return self.open_fd_stdout()

    def open_fd_arg(self) -> IO:
        """Open a file descriptor supplied in GETARGS."""
        self._fd: IO = self.arg_export_fd
        self._fd_close: bool = self.arg_export_fd_close
        self._fd_info: str = f"{self._fd}"
        self.echo(msg=f"Exporting to {self._fd_info}")
        return self._fd

    @property
    def export_full_path(self) -> pathlib.Path:
        """Pass."""
        return get_paths_format(
            self.arg_export_path, self.arg_export_file, mapping=self.export_templates
        )

    def open_fd_path(self) -> IO:
        """Open a file descriptor for a path."""
        export_fd_close = self.arg_export_fd_close
        export_backup = self.arg_export_backup
        export_overwrite = self.arg_export_overwrite

        self._file_path: pathlib.Path = self.export_full_path
        self._file_path_backup: Optional[pathlib.Path] = None
        self._fd_close: bool = export_fd_close

        check_path_is_not_dir(path=self._file_path)

        if self._file_path.exists():
            if export_backup:
                self._file_path_backup: pathlib.Path = path_backup_file(path=self._file_path)
                self._file_mode: str = "Renamed existing file and created new file"
                self.echo(
                    msg=f"Renamed existing file to {str(self._file_path_backup)!r}",
                    debug=True,
                )
            elif not export_overwrite:
                msg = f"Export file {str(self._file_path)!r} already exists and overwrite is False!"
                self.echo(msg=msg, error=ApiError, level="error")
            else:
                self._file_mode: str = "Overwrote existing file"
        else:
            self._file_mode: str = "Created new file"

        if not self._file_path.parent.is_dir():
            self._file_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            self.echo(msg=f"Created directory {str(self._file_path.parent)!r}", debug=True)

        if not self._file_path.exists():
            self._file_path.touch(mode=0o600)
            self.echo(msg=f"Created new file {str(self._file_path)!r}", debug=True)

        self._fd_info: str = f"file {str(self._file_path)!r} ({self._file_mode})"
        self.echo(msg=f"Exporting to {self._fd_info}")

        self._fd: IO = self._file_path.open(mode="w", encoding="utf-8")
        return self._fd

    def open_fd_stdout(self) -> IO:
        """Open a file descriptor to STDOUT."""
        self._fd_close: bool = False
        self._fd: IO = sys.stdout
        self._fd_info: str = "stdout"
        self.echo(msg=f"Exporting to {self._fd_info}")
        return self._fd

    def close_fd(self):
        """Close a file descriptor."""
        self._fd.write("\n")
        close = getattr(self, "_fd_close", False)
        closer = getattr(self._fd, "close", None)

        if close and callable(closer):
            closer()

        self.echo(msg=f"Finished exporting to {self._fd_info}")

    @property
    def export_templates(self) -> dict:
        """Pass."""
        return self.STORE.get("export_templates") or {}

    @property
    def arg_export_fd(self) -> Optional[IO]:
        """Pass."""
        return self.get_arg_value("export_fd")

    @property
    def arg_export_file(self) -> Optional[PathLike]:
        """Pass."""
        value = self.get_arg_value("export_file")
        if isinstance(value, (str, pathlib.Path)) and value:
            return value
        return None

    @property
    def arg_export_path(self) -> pathlib.Path:
        """Pass."""
        value = self.get_arg_value("export_path")
        return get_path(obj=value)

    @property
    def arg_export_backup(self) -> bool:
        """Pass."""
        return self.get_arg_value("export_backup")

    @property
    def arg_export_overwrite(self) -> bool:
        """Pass."""
        return self.get_arg_value("export_overwrite")

    @property
    def arg_export_fd_close(self) -> bool:
        """Pass."""
        return self.get_arg_value("export_fd_close")


ARG_DESCRIPTIONS: dict = {
    "field_excludes": "Fields to exclude from output",
    "field_flatten": "Flatten complex fields",
    "field_explode": "Field to explode",
    "field_titles": "Rename fields to titles",
    "field_compress": "Shorten field names in output to 'adapter:field'",
    "field_replace": "Field name character replacements",
    "field_join": "Join list field values",
    "field_join_value": "Join list field values using",
    "field_join_trim": "Join list field character limit (0 = None)",
    "field_null": "Add null values for missing fields",
    "field_null_value": "Null value to use for missing simple fields",
    "field_null_value_complex": "Null value to use for missing complex fields",
    "tags_add": "Tags to add to assets",
    "tags_add_invert_selection": "Invert selection for tags to add",
    "tags_remove": "Tags to remove from assets",
    "tags_remove_invert_selection": "Invert selection for tags to remove",
    "report_adapters_missing": "Add Missing Adapters calculation",
    "report_software_whitelist": "Missing Software to calculate",
    "page_progress": "Echo page progress every N assets",
    "do_echo": "Echo messages to console",
    "custom_cbs": "Custom callbacks to perform on assets",
    "json_flat": "For JSON Export: Use JSONL format",
    "csv_key_miss": "For CSV Export: Value to use when keys are missing",
    "csv_key_extras": "For CSV Export: What to do with extra CSV columns",
    "csv_dialect": "For CSV Export: CSV Dialect to use",
    "csv_quoting": "For CSV Export: CSV quoting style",
    "csv_field_flatten": "For CSV/XLSX Export: Enable flattening of complex fields",
    "csv_field_join": "For CSV/XLSX Export: Enable joining of list fields",
    "csv_field_null": "For CSV/XLSX Export: Enable null values for missing fields",
    "export_file": "File to export data to",
    "export_path": "Directory to export data to",
    "export_overwrite": "Overwrite export_file if it exists",
    "export_schema": "Export schema of fields",
    "export_fd": "Export to a file descriptor",
    "export_fd_close": "Close the file descriptor when done",
    "export_backup": "If export_file exists, rename it with the datetime",
    "table_format": "For Table export: Table format to use",
    "table_max_rows": "For Table export: Maximum rows to output",
    "table_api_fields": "For Table export: Include API fields in output",
    "xlsx_column_length": "For XLSX export: Length to use for every column",
    "xlsx_cell_format": "For XLSX Export: Formatting to apply to every cell",
    "debug_timing": "Enable logging of time taken for each callback",
    "explode_entities": "Split rows into one row for each asset entity",
    "include_dates": "Include history date and current date as a columns in the output",
}
"""Descriptions of all arguments for all callbacks"""
