# -*- coding: utf-8 -*-
"""JSON export callbacks class."""
import json
import textwrap
from typing import List, Union

from ...tools import listify
from .base import Base


class Json(Base):
    """JSON export callbacks class.

    See Also:
        See :meth:`args_map` and :meth:`args_map_custom` for details on the extra kwargs that can
        be passed to :meth:`axonius_api_client.api.assets.users.Users.get` or
        :meth:`axonius_api_client.api.assets.devices.Devices.get`

    """

    CB_NAME: str = "json"
    """name for this callback"""

    @classmethod
    def args_map_custom(cls) -> dict:
        """Get the custom argument names and their defaults for this callbacks object.

        See Also:
            :meth:`args_map_export` for the export arguments for this callbacks object.

            :meth:`args_map` for the arguments for all callback objects.

        Notes:
            These arguments can be supplied as extra kwargs passed to
            :meth:`axonius_api_client.api.assets.users.Users.get` or
            :meth:`axonius_api_client.api.assets.devices.Devices.get`

        """
        args = {}
        args.update(cls.args_map_export())
        args.update({"json_flat": False})
        return args

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Json, self).start(**kwargs)
        flat = self.get_arg_value("json_flat")

        self._first_row = True
        self.open_fd()
        begin = "" if flat else "["
        self._fd.write(begin)

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        super(Json, self).stop(**kwargs)
        flat = self.get_arg_value("json_flat")

        self.do_export_schema()
        end = "" if flat else "\n]"
        self._fd.write(end)
        self.close_fd()

    def process_row(self, row: Union[List[dict], dict]) -> List[dict]:
        """Process the callbacks for current row.

        Args:
            row: row to process
        """
        rows = listify(row)
        rows = self.do_pre_row(rows=rows)
        row_return = [{"internal_axon_id": row["internal_axon_id"]} for row in rows]
        rows = self.do_row(rows=rows)
        self.write_rows(rows=rows)
        del rows, row
        return row_return

    def write_rows(self, rows: Union[List[dict], dict]):
        """Write rows to the file descriptor.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        flat = self.get_arg_value("json_flat")

        indent = None if flat else 2
        prefix = " " * indent if indent else ""

        for row in rows:
            if self._first_row:
                pre = "" if flat else "\n"
            else:
                pre = "\n" if flat else ",\n"

            self._first_row = False
            self._fd.write(pre)

            value = json.dumps(row, indent=indent)
            value = textwrap.indent(value, prefix=prefix) if indent else value
            self._fd.write(value)
            del value, row

    def do_export_schema(self):
        """Add schema rows to the output."""
        export_schema = self.get_arg_value("export_schema")

        if export_schema:
            row = {"schemas": self.final_schemas}
            self.write_rows(rows=row)
            del row
