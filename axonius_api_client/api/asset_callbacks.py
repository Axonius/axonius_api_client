# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import codecs
import csv
import os
import re
import sys

from .. import cli, constants, exceptions, tools


class Callbacks(object):
    """Object for handling callbacks for assets."""

    MAP_ROW = {
        "first_page": {"idx": 100, "run_once": True},
        "field_nulls": {"idx": 200},
        "field_flatten": {"idx": 300},
        "field_excludes": {"idx": 400},
        "field_joiner": {"idx": 500},
        "field_titles": {"idx": 600},
        "export_json": {
            "conflicts": ["export_csv"],
            "idx": 10000,
            "start": ["export_json_start"],
            "stop": ["export_json_stop"],
        },
        "export_csv": {
            "conflicts": ["export_json"],
            "runs": ["field_nulls", "field_flatten", "field_joiner", "field_titles"],
            "idx": 10000,
            # "start": ["export_csv_start"],
            "stop": ["export_csv_stop"],
        },
    }
    ALWAYS_FIELDS = ["internal_axon_id", "adapters", "adapter_list_length"]

    def __init__(self, apiobj, all_fields, getargs, store, state):
        """Object for handling callbacks for assets."""
        self.LOG = apiobj._log.getChild(self.__class__.__name__)

        fields = store["fields"]
        fields = [x for x in self.ALWAYS_FIELDS if x not in fields] + fields
        self.APIOBJ = apiobj
        self.FIELDS_ALL = all_fields
        self.FIELDS = fields
        self.STORE = store
        self.STATE = state
        self.GETARGS = getargs
        self.SCHEMAS = apiobj.fields.get_schemas(fields=fields, all_fields=all_fields)
        self.SCHEMAS_PRETTY = apiobj.fields.pretty_schemas(schemas=self.SCHEMAS)
        self.SCHEMAS_ALL = apiobj.fields.get_schemas_flat(all_fields=all_fields)
        self.SCHEMAS_EXTRA = []  # XXX special method per cb that adds schemas?
        self.ERROR = getargs.get("callback_error", True)
        self.CALLBACKS_RAN = []
        self.CALLBACKS_RAN_ONCE = []
        self.CALLBACKS = tools.listify(getargs.get("callbacks", []))
        self.ECHO_OK = getargs.get("echo_ok", cli.context.click_echo_ok)
        self.run_map
        self.get_field_schemas()

    def get_field_schemas(self, flat=False):
        """Get the schemas for keys that will be in each row."""
        schemas = []

        for field, schema in self.SCHEMAS.items():
            if self._is_excluded(field=field):
                continue

            if flat or "field_flatten" in self.run_map["row"]:
                if schema["is_complex"]:
                    for sub_field, sub_schema in schema["sub_fields"].items():
                        if not sub_schema["is_root"]:
                            continue
                        schemas.append(sub_schema)
                else:
                    schemas.append(schema)
            else:
                schemas.append(schema)

        return schemas

    @property
    def run_map(self):
        """Get the map of all callbacks that will be run."""
        if hasattr(self, "_run_map"):
            return self._run_map

        row_maps = self.MAP_ROW
        self._run_map = run_map = {"start": [], "stop": [], "row": []}

        for callback in self.CALLBACKS:
            self._check_cb_map(callback=callback)
            self._check_cb_method(callback=callback)

            if callback not in run_map["row"]:
                run_map["row"].append(callback)

            cb_map = row_maps[callback]

            for end in ["start", "stop"]:
                bookends = cb_map.get(end, [])
                bookends = [x for x in bookends if x not in run_map[end]]
                for bookend in bookends:
                    self._check_cb_method(callback=callback)
                    run_map[end].append(bookend)

        for callback in run_map["row"]:
            cb_map = row_maps[callback]
            cb_conflicts = cb_map.get("conflicts", [])
            cb_runs = cb_map.get("runs", [])
            run_map["row"] = [x for x in run_map["row"] if x not in cb_runs]

            conflicts = [x for x in cb_conflicts if x in run_map["row"]]

            if conflicts:
                msg = "Callback {!r} conflicts with {!r}".format(callback, conflicts)
                raise exceptions.ApiError(msg)

        run_map["row"] = sorted(run_map["row"], key=lambda x: row_maps[x].get("idx", 10))

        return self._run_map

    def start(self, **kwargs):
        """Run start callbacks."""
        self.LOG.debug("Starting {}".format(self))
        self.LOG.debug("Start run map {}".format(self.run_map))
        schemas = [x["name_qual"] for x in self.get_field_schemas()]
        self.LOG.debug("Start field schemas {}".format(schemas))

        for callback in self.run_map["start"]:
            self.run(callback=callback)

    def stop(self, **kwargs):
        """Run stop callbacks."""
        self.LOG.debug("Stopping {}".format(self))
        self.LOG.debug("Stop run map {}".format(self.run_map))
        for callback in self.run_map["stop"]:
            self.run(callback=callback)

    def row(self, row):
        """Handle callbacks for an asset."""
        for callback in self.run_map["row"]:
            row = self.run(callback=callback, row=row)
        return row

    def run(self, callback, row=None):
        """Run a callback."""
        cb_map = self.MAP_ROW.get(callback, {})
        run_once = cb_map.get("run_once", False)

        if run_once:
            if callback not in self.CALLBACKS_RAN_ONCE:
                self.CALLBACKS_RAN_ONCE.append(callback)
            else:
                return row

        if callback not in self.CALLBACKS_RAN:
            self.CALLBACKS_RAN.append(callback)

        self.log_once(
            msg="Running callback {!r} map: {}".format(callback, cb_map), level="debug"
        )

        try:
            method = getattr(self, callback)
            return method(row=row)
        except Exception:
            self.LOG.exception(
                "Callback {!r} failed!\nmap: {}\nrow: {}".format(callback, cb_map, row)
            )
            if self.ERROR:
                raise

        return row

    def first_page(self, row):
        """Asset callback to echo first page info using an echo method."""
        info = "{rows_page} rows (total rows {rows_total}, total pages {page_total})"
        info = info.format(**self.STATE)
        self.ECHO_OK("First page received! {}".format(info))

        query = self.STATE.get("query", "") or ""
        self.ECHO_OK("Query: {}".format(query))

        joiner = "\n   - "
        schemas = joiner + joiner.join(self.SCHEMAS_PRETTY)
        self.ECHO_OK("Fields: {}".format(schemas))
        return row

    def field_nulls(self, row):
        """Asset callback to add None values to fields not returned."""
        null_value = self.GETARGS.get("null_value", None)

        def nuller(field, schema, row, null_value):
            """Null out missing fields."""
            if schema["is_complex"]:
                row[field] = row.get(field, [])
                for entry in row[field]:
                    for sub_field, sub_schema in schema["sub_fields"].items():
                        nuller(
                            field=sub_field,
                            schema=sub_schema,
                            row=entry,
                            null_value=null_value,
                        )
            else:
                row[field] = row.get(field, null_value)

        for field, schema in self.SCHEMAS.items():
            nuller(row=row, field=field, schema=schema, null_value=null_value)
        return row

    def _is_excluded(self, field):
        if not hasattr(self, "_excludes"):
            self._excludes = self.GETARGS.get("field_excludes", [])
            self._excludes = tools.listify(obj=self._excludes)
            self._excludes = [
                i.strip() for f in self._excludes for i in f.split(",") if i.strip()
            ]
            self._exclude_res = [re.compile(x, re.I) for x in self._excludes]

        for exclude in self._exclude_res:
            if exclude.match(field):
                return True
        return False

    def field_excludes(self, row):
        """Asset callback to remove fields from row."""
        for field in list(row):
            if self._is_excluded(field=field) and field in row:
                row.pop(field)
        return row

    def field_joiner(self, row):
        """Join values."""
        joiner = self.GETARGS.get("joiner", constants.FIELD_JOINER)
        trim_len = self.GETARGS.get("joiner_trim_len", constants.FIELD_TRIM_LEN)
        trim_str = constants.FIELD_TRIM_STR

        for field in row:
            if isinstance(row[field], constants.LIST):
                row[field] = joiner.join([format(x) for x in row[field]])

            if trim_len and isinstance(row[field], constants.STR):
                field_len = len(row[field])
                if len(row[field]) >= trim_len:
                    msg = trim_str.format(field_len=field_len, trim_len=trim_len)
                    row[field] = joiner.join([row[field][:trim_len], msg])
        return row

    def field_titles(self, row):
        """Asset callback to change titles to title."""
        for field in list(row):
            if field in self.SCHEMAS_ALL:
                schema = self.SCHEMAS_ALL[field]
                title = schema["column_title"]
                row[title] = row.pop(field)
        return row

    def log_once(self, msg, level="debug"):
        """Log a message just once."""
        if not hasattr(self, "_logged"):
            self._logged = []

        method = getattr(self.LOG, level, "debug")
        log_once = self.GETARGS.get("log_once", True)

        if msg in self._logged:
            do_log = not log_once
        else:
            self._logged.append(msg)
            do_log = True

        if do_log:
            method(msg)

    def field_flatten(self, row):
        """Asset callback to flatten complex fields."""
        null_value = self.GETARGS.get("null_value", None)

        for field, schema in self.SCHEMAS.items():
            if field not in row:
                continue

            if schema["is_complex"]:
                items = row.pop(field, []) or []

                for sub_field, sub_schema in schema["sub_fields"].items():
                    if not sub_schema["is_root"]:
                        continue

                    sub_name_qual = sub_schema["name_qual"]
                    sub_name = sub_schema["name"]

                    if sub_name_qual in row:
                        msg = "overwriting sub_field {!r}".format(sub_name_qual)
                        self.log_once(msg=msg, level="warning")

                    row[sub_name_qual] = []

                    for item in items:
                        value = item.get(sub_name, null_value)

                        if isinstance(value, constants.LIST):
                            row[sub_name_qual] += value
                        else:
                            row[sub_name_qual].append(value)
        return row

    def export_json_start(self, **kwargs):
        """Start export_json by creating jsonstream and associated file descriptor."""
        self.open_fd()
        self._jsonstream = cli.serial.JsonStream(fd=self._fd)

    def export_json_stop(self, **kwargs):
        """Finish export_json by closing jsonstream and associated file descriptor."""
        # XXX could do schema addition here
        self._jsonstream.close()
        self.close_fd()

    def export_json(self, row):
        """Write row to jsonstreams and delete it."""
        self._jsonstream.write(row)
        del row

    # def export_csv_start(self, **kwargs):
    #     """Start export_csv by creating dictwriter and associated file descriptor."""

    def export_csv_stop(self, **kwargs):
        """Finish export_csv by closing dictwriter and associated file descriptor."""
        self.close_fd()

    def _get_explode(self, explode):
        if explode:
            base_schemas = {x["name_base"]: x for x in self.SCHEMAS.values()}
            if explode in base_schemas:
                return base_schemas[explode]

            msg = "Explode field {!r} not found, valid fields:{}"
            msg = msg.format(explode, list(base_schemas))
            raise exceptions.ApiError(msg)

    def export_csv(self, row):
        """Write row to dictwriter and delete it."""
        if not hasattr(self, "_csv_schemas"):
            self._csv_schemas = self.get_field_schemas(flat=True)
            # custom_schemas = [
            #     {"column_title": "test", "name_qual": "", "type_norm": ""}
            # ]
            # self._csv_schemas += getattr(self, "_custom_schemas", custom_schemas)
        # XXX restval, dialect

        if not hasattr(self, "_csvstream"):
            export_schema = self.GETARGS.get("export_schema", True)
            quote = self.GETARGS.get("csv_quoting", csv.QUOTE_NONNUMERIC)
            explode = self.GETARGS.get("explode_field", None)

            self._explode_schema = self._get_explode(explode=explode)

            titles = []
            names = []
            types = []

            for schema in self._csv_schemas:
                titles.append(schema["column_title"])
                names.append(schema.get("name_qual", ""))
                types.append(schema.get("type_norm", ""))
            # import pprint

            # pprint.pprint(self._explode_schema)
            self.open_fd()
            self._fd.write(codecs.BOM_UTF8.decode("utf-8"))
            self._csvstream = csv.DictWriter(self._fd, fieldnames=titles, quoting=quote)
            self._csvstream.writerow(dict(zip(titles, titles)))

            if export_schema:
                self._csvstream.writerow(dict(zip(titles, names)))
                self._csvstream.writerow(dict(zip(titles, types)))

        # row["test"] = "diaf"
        # row.pop("specific_data.data.network_interfaces", None)
        row = self.run(callback="field_nulls", row=row)

        # print(pprint.pformat(row))
        row = self.run(callback="field_flatten", row=row)
        # explode here
        row = self.run(callback="field_joiner", row=row)
        row = self.run(callback="field_titles", row=row)
        self._csvstream.writerow(row)
        del row

    # def field_explode(self, row):
    #     """Explode a field into multiple rows."""
    #     schema = self._explode_schema
    #     rows = []

    def open_fd(self):
        """Open a file descriptor."""
        self._export_file = self.GETARGS.get("export_file", None)
        self._export_path = self.GETARGS.get("export_path", os.getcwd())
        self._export_overwrite = self.GETARGS.get("export_overwrite", False)
        self._file_path = None
        if "export_fd" in self.GETARGS:
            self._fd = self.GETARGS["export_fd"]
            self._fd_close = self.GETARGS.get("export_fd_close", False)
            self.LOG.debug("Using supplied descriptor {}".format(self._fd))
        elif self._export_file:
            path = tools.path(obj=self._export_path)
            path.mkdir(mode=0o700, parents=True, exist_ok=True)
            self._file_path = path / self._export_file
            self._file_mode = "overwrote" if self._file_path.exists() else "created"

            if self._file_path.exists() and not self._export_overwrite:
                msg = "Export file {p} already exists and export-overwite is False!"
                msg = msg.format(p=self._file_path)
                self._echo_error(msg)

            self._file_path.touch(mode=0o600)
            self._fd_close = True
            self._fd = self._file_path.open(mode="w")
            self.LOG.debug("Opened file descriptor {}".format(self._fd))
        else:
            self._fd_close = False
            self._fd = sys.stdout
            self.LOG.debug("Using stdout descriptor {}".format(self._fd))
        return self._fd

    def close_fd(self):
        """Close a file descriptor."""
        if self._fd_close:
            self.LOG.debug("Closing descriptor {}".format(self._fd))
            self._fd.close()
            if self._file_path:
                msg = "Exported assets to path {!r} ({} file)"
                msg = msg.format(format(self._file_path), self._file_mode)
                self.ECHO_OK(msg)

    def _check_cb_map(self, callback):
        if callback not in self.MAP_ROW:
            msg = "Callback {!r} is not in callback map: {!r}"
            msg = msg.format(callback, list(self.MAP_ROW))
            raise exceptions.ApiError(msg)

    def _check_cb_method(self, callback):
        if not hasattr(self, callback):
            msg = "Callback {!r} is not a method on: {!r}"
            msg = msg.format(callback, self)
            raise exceptions.ApiError(msg)

    def __str__(self):
        """Show info for this object."""
        msg = "{c.__module__}.{c.__name__}(callbacks={cbs}, ran={ran})"
        return msg.format(c=self.__class__, cbs=self.CALLBACKS, ran=self.CALLBACKS_RAN)

    def __repr__(self):
        """Show info for this object."""
        return self.__str__()

    # XXX what happens if new key added??

    # XXX CB for missing adapters report
    # XXX CB for expand rows

    # XXX cnx get raw config
    # XXX cnx add json config
    # XXX cnx add: take in json via stdin or file to create connections
    # XXX fields get CLI needs to add at least title (maybe normtype too?)
    # XXX figure way to have csv/json export return asset instead of deleting it?
    #     probably need a whole diff callback
