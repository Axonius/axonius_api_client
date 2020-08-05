# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import json
import textwrap
from typing import List

from ...tools import listify
from .base import Base

JSON_FLAT: bool = False


class Json(Base):
    """Pass."""

    CB_NAME: str = "json"

    def start(self, **kwargs):
        """Create jsonstream and associated file descriptor."""
        super(Json, self).start(**kwargs)
        flat = self.GETARGS.get("json_flat", JSON_FLAT)

        self._first_row = True
        self.open_fd()
        begin = "" if flat else "["
        self._fd.write(begin)

    def stop(self, **kwargs):
        """Close jsonstream and associated file descriptor."""
        super(Json, self).stop(**kwargs)
        flat = self.GETARGS.get("json_flat", JSON_FLAT)

        self.do_export_schema()
        end = "" if flat else "\n]"
        self._fd.write(end)
        self.close_fd()

    def process_row(self, row: dict) -> List[dict]:
        """Write row to jsonstreams and delete it."""
        self.do_pre_row()

        return_row = [{"internal_axon_id": row["internal_axon_id"]}]

        new_rows = self.do_row(row=row)

        for new_row in listify(new_rows):
            self.write_row(row=new_row)
            del new_row

        del new_rows
        del row

        return return_row

    def write_row(self, row: dict):
        """Pass."""
        flat = self.GETARGS.get("json_flat", JSON_FLAT)

        indent = None if flat else 2
        prefix = " " * indent if indent else ""

        if flat:
            pre = "" if self._first_row else "\n"
        else:
            pre = "\n" if self._first_row else ",\n"

        self._first_row = False
        self._fd.write(pre)

        value = json.dumps(row, indent=indent)
        value = textwrap.indent(value, prefix=prefix) if indent else value
        self._fd.write(value)
        del value

    def do_export_schema(self):
        """Pass."""
        export_schema = self.GETARGS.get("export_schema", False)

        if export_schema:
            row = {"schemas": self.final_schemas}
            self.write_row(row=row)
            del row
