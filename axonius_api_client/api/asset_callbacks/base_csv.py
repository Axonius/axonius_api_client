# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import codecs
import csv

from ...tools import listify
from .base import Base


class Csv(Base):
    """Pass."""

    CB_NAME = "csv"

    def start(self, **kwargs):
        """Create csvstream and associated file descriptor."""
        self._pre_start(**kwargs)
        super(Csv, self).start(**kwargs)
        print("high")
        self._start(**kwargs)

    def _pre_start(self, **kwargs):
        """Pass."""
        self.GETARGS["field_null"] = True
        self.GETARGS["field_flatten"] = True
        self.GETARGS["field_join"] = True
        if self.GETARGS.get("field_titles", None) is None:
            self.GETARGS["field_titles"] = True

    def _start(self, **kwargs):
        restval = self.GETARGS.get("csv_key_miss", None)
        dialect = self.get_csv_dialect()
        quote = self.get_csv_quote()

        self.open_fd()
        self._fd.write(codecs.BOM_UTF8.decode("utf-8"))
        self._stream = csv.DictWriter(
            self._fd,
            fieldnames=self.columns_final,
            quoting=quote,
            lineterminator="\n",
            restval=restval,
            dialect=dialect,
        )
        self._stream.writerow(dict(zip(self.columns_final, self.columns_final)))
        self.do_export_schema()

    def stop(self, **kwargs):
        """Close dictwriter and associated file descriptor."""
        super(Csv, self).stop(**kwargs)
        self._stop(**kwargs)

    def _stop(self, **kwargs):
        self._fd.write("\n")
        self.close_fd()

    def process_row(self, row):
        """Write row to dictwriter and delete it."""
        row_return = [{"internal_axon_id": row["internal_axon_id"]}]

        new_rows = self._process_row(row=row)

        for new_row in listify(new_rows):
            self._stream.writerow(new_row)
            del new_row

        del new_rows
        del row

        return row_return

    def get_csv_dialect(self):
        """Pass."""
        dialect = self.GETARGS.get("csv_dialect", "excel")
        return dialect

    def get_csv_quote(self):
        """Pass."""
        quote = self.GETARGS.get("csv_quoting", "nonnumeric")
        quote = getattr(csv, f"QUOTE_{quote.upper()}")
        return quote

    def do_export_schema(self):
        """Pass."""
        export_schema = self.GETARGS.get("export_schema", True)

        if export_schema:
            titles = [x["column_title"] for x in self.schemas_final]
            names = [x["name_qual"] for x in self.schemas_final]
            types = [x["type_norm"] for x in self.schemas_final]
            if self.GETARGS["field_titles"]:
                self._stream.writerow(dict(zip(self.columns_final, names)))
                self._stream.writerow(dict(zip(self.columns_final, types)))
            else:
                self._stream.writerow(dict(zip(self.columns_final, titles)))
                self._stream.writerow(dict(zip(self.columns_final, types)))
