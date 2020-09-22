# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import codecs
import csv
from typing import List

from ...tools import listify
from .base import Base


class Csv(Base):
    """Pass."""

    CB_NAME: str = "csv"

    def _init(self, **kwargs):
        """Pass."""
        self.GETARGS["field_null"] = True
        self.GETARGS["field_flatten"] = True
        self.GETARGS["field_join"] = True
        if self.GETARGS.get("field_titles", None) is None:
            self.GETARGS["field_titles"] = True

    def start(self, **kwargs):
        """Create csvstream and associated file descriptor."""
        super(Csv, self).start(**kwargs)
        self.open_fd()

    def do_start(self, **kwargs):
        """Pass."""
        if getattr(self, "_stream", None):
            return

        restval = self.GETARGS.get("csv_key_miss", None)
        extras = self.GETARGS.get("csv_key_extras", "ignore")
        dialect = self.get_csv_dialect()
        quote = self.get_csv_quote()

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
        """Close dictwriter and associated file descriptor."""
        super(Csv, self).stop(**kwargs)
        self.do_stop(**kwargs)

    def do_stop(self, **kwargs):
        """Pass."""
        self._fd.write("\n")
        self.close_fd()

    def write_row(self, row: dict):
        self._stream.fieldnames += [x for x in row if x not in self._stream.fieldnames]
        self._stream.writerow(row)

    def process_row(self, row: dict) -> List[dict]:
        """Write row to dictwriter and delete it."""
        self.do_pre_row(row=row)
        self.do_start()

        row_return = [{"internal_axon_id": row["internal_axon_id"]}]
        new_rows = self.do_row(row=row)

        for new_row in listify(new_rows):
            self.write_row(row=new_row)
            del new_row

        del new_rows
        del row

        return row_return

    def get_csv_dialect(self) -> str:
        """Pass."""
        dialect = self.GETARGS.get("csv_dialect", "excel")
        return dialect

    def get_csv_quote(self) -> int:
        """Pass."""
        quote = self.GETARGS.get("csv_quoting", "nonnumeric")
        quote = getattr(csv, f"QUOTE_{quote.upper()}")
        return quote

    def do_export_schema(self):
        """Pass."""
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
