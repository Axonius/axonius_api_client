# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import json
import tempfile

from ...tools import listify
from .base_csv import Csv


class JsonToCsv(Csv):
    """Pass."""

    CB_NAME = "json_to_csv"

    def start(self, **kwargs):
        """Create temp file for writing to."""
        super(Csv, self).start(**kwargs)
        self._temp_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        self.echo(msg=f"Writing JSON to temporary file {self._temp_file.name!r}")

    def stop(self, **kwargs):
        """Create CSV file, process each row in temp file, then close temp and csv."""
        super(Csv, self).stop(**kwargs)
        self._start(**kwargs)

        self.echo(msg="Re-reading temporary file and converting to CSV")
        self._temp_file.file.seek(0)
        for line in self._temp_file.file.readlines():
            row = json.loads(line.strip())
            rows = super(Csv, self).row(row=row)
            for row_new in listify(rows):
                self._stream.writerow(row_new)
                del row_new
            del rows

        self.echo(msg=f"Closing and deleting temporary file {self._temp_file.name!r}")
        self._temp_file.file.close()
        self._stop(**kwargs)

    def row(self, row):
        """Write row to temp file with no processing."""
        self.first_page()
        return_row = [{"internal_axon_id": row["internal_axon_id"]}]
        row = json.dumps(row)
        self._temp_file.file.write(f"{row}\n")
        del row
        return return_row
