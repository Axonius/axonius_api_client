# -*- coding: utf-8 -*-
"""JSON to CSV export callbacks class."""
import json
import tempfile
from typing import List, Union

from ...tools import listify
from .base_csv import Csv


class JsonToCsv(Csv):
    """JSON to CSV export callbacks class."""

    CB_NAME: str = "json_to_csv"
    """name for this callback"""

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Csv, self).start(**kwargs)
        self.open_fd()
        self._temp_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        self.echo(msg=f"Writing JSON to temporary file {self._temp_file.name!r}")

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        self.STATE["rows_processed_total"] = 0
        self.do_start(**kwargs)

        self.echo(msg="Re-reading temporary file and converting to CSV")
        self._temp_file.file.seek(0)

        for line in self._temp_file.file.readlines():
            row = json.loads(line.strip())
            rows = listify(row)
            rows = self.do_pre_row(rows=rows)
            rows = self.do_row(rows=rows)
            self.write_rows(rows=rows)
            del rows, row, line

        self.echo(msg=f"Closing and deleting temporary file {self._temp_file.name!r}")
        self._temp_file.file.close()
        super(JsonToCsv, self).stop(**kwargs)

    def process_row(self, row: Union[List[dict], dict]) -> List[dict]:
        """Process the callbacks for current row.

        Args:
            row: row to process
        """
        rows = listify(row)

        row_return = [{"internal_axon_id": row["internal_axon_id"]} for row in rows]
        rows = self.do_pre_row(rows=rows)
        for row in rows:
            value = json.dumps(row)
            self._temp_file.file.write(f"{value}\n")
            del row, value

        return row_return
