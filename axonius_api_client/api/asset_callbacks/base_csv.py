# -*- coding: utf-8 -*-
"""CSV export callbacks class."""
import codecs
import csv
from typing import List, Union

from ...tools import listify
from .base import Base


class Csv(Base):
    """CSV export callbacks class."""

    CB_NAME: str = "csv"
    """name for this callback"""

    def _init(self, **kwargs):
        """Override defaults in GETARGS to make export readable."""
        self.GETARGS["field_null"] = True
        self.GETARGS["field_flatten"] = True
        self.GETARGS["field_join"] = True
        if self.GETARGS.get("field_titles", None) is None:
            self.GETARGS["field_titles"] = True

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Csv, self).start(**kwargs)
        self.open_fd()

    def do_start(self, **kwargs):
        """Create the CSV writer and write the columns."""
        if getattr(self, "_stream", None):
            return

        restval = self.GETARGS.get("csv_key_miss", None)
        extras = self.GETARGS.get("csv_key_extras", "ignore")
        dialect = self.GETARGS.get("csv_dialect", "excel")
        quote = self.GETARGS.get("csv_quoting", "nonnumeric")
        quote = getattr(csv, f"QUOTE_{quote.upper()}")

        try:
            self._fd.write(codecs.BOM_UTF8.decode("utf-8"))
        except Exception:  # pragma: no cover
            # only happens on windows sometimes
            self.LOG.error("Unable to write UTF8 BOM!")

        self._stream = csv.DictWriter(
            self._fd,
            fieldnames=self.final_columns,
            quoting=quote,
            lineterminator="\n",
            restval=restval,
            dialect=dialect,
            extrasaction=extras,
        )
        self._stream.writerow(dict(zip(self.final_columns, self.final_columns)))
        self.do_export_schema()

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        super(Csv, self).stop(**kwargs)
        self.do_stop(**kwargs)

    def do_stop(self, **kwargs):
        """Close the file descriptor."""
        self._fd.write("\n")
        self.close_fd()

    def write_rows(self, rows: Union[List[dict], dict]):
        """Write rows to the file descriptor.

        Args:
            rows: rows to process
        """
        rows = listify(rows)
        for row in rows:
            self._stream.fieldnames += [x for x in row if x not in self._stream.fieldnames]
            self._stream.writerow(row)

    def process_row(self, row: Union[List[dict], dict]) -> List[dict]:
        """Process the callbacks for current row.

        Args:
            row: row to process
        """
        rows = listify(row)
        self.do_start()

        row_return = [{"internal_axon_id": row["internal_axon_id"]} for row in rows]
        rows = self.do_pre_row(rows=rows)
        rows = self.do_row(rows=rows)
        self.write_rows(rows=rows)
        del rows, row
        return row_return

    def do_export_schema(self):
        """Add schema rows to the output."""
        export_schema = self.GETARGS.get("export_schema", True)

        if export_schema:
            titles = [x["column_title"] for x in self.final_schemas]
            names = [x["name_qual"] for x in self.final_schemas]
            types = [x["type_norm"] for x in self.final_schemas]
            if self.GETARGS["field_titles"]:
                self._stream.writerow(dict(zip(self.final_columns, names)))
                self._stream.writerow(dict(zip(self.final_columns, types)))
            else:
                self._stream.writerow(dict(zip(self.final_columns, titles)))
                self._stream.writerow(dict(zip(self.final_columns, types)))
