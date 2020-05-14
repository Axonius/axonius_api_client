# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import codecs
import csv

from ...tools import listify
from .base import Base


class Csv(Base):
    """Pass."""

    CB_NAME = "csv"

    def row(self, row):
        """Write row to dictwriter and delete it."""
        row_return = [{"internal_axon_id": row["internal_axon_id"]}]

        rows = super(Csv, self).row(row=row)

        for row_new in listify(rows):
            self._stream.writerow(row_new)
            del row_new

        del rows
        del row

        return row_return

    def start(self, **kwargs):
        """Create csvstream and associated file descriptor."""
        super(Csv, self).start(**kwargs)
        self._start(**kwargs)

    def _start(self, **kwargs):
        self.GETARGS["field_null"] = True
        self.GETARGS["field_flatten"] = True
        self.GETARGS["field_join"] = True
        if self.GETARGS.get("field_titles", None) is None:
            self.GETARGS["field_titles"] = True

        restval = self.GETARGS.get("csv_key_miss", None)
        dialect = self.get_csv_dialect()
        quote = self.get_csv_quote()

        final = self.schemas_final(flat=True)
        if self.GETARGS["field_titles"]:
            titles = [x["column_title"] for x in final]
        else:
            titles = [x["name_qual"] for x in final]

        self.open_fd()
        self._fd.write(codecs.BOM_UTF8.decode("utf-8"))
        self._stream = csv.DictWriter(
            self._fd,
            fieldnames=titles,
            quoting=quote,
            lineterminator="\n",
            restval=restval,
            dialect=dialect,
        )
        self._stream.writerow(dict(zip(titles, titles)))
        self.do_export_schema(final=final)

    def get_csv_dialect(self):
        """Pass."""
        dialect = self.GETARGS.get("csv_dialect", "excel")
        return dialect

    def get_csv_quote(self):
        """Pass."""
        quote = self.GETARGS.get("csv_quoting", "nonnumeric")
        quote = getattr(csv, f"QUOTE_{quote.upper()}")
        return quote

    def do_export_schema(self, final):
        """Pass."""
        export_schema = self.GETARGS.get("export_schema", True)

        if export_schema:
            if self.GETARGS["field_titles"]:
                titles = [x["column_title"] for x in final]
                names = [x["name_qual"] for x in final]
                types = [x["type_norm"] for x in final]
                self._stream.writerow(dict(zip(titles, names)))
                self._stream.writerow(dict(zip(titles, types)))
            else:
                titles = [x["column_title"] for x in final]
                names = [x["name_qual"] for x in final]
                types = [x["type_norm"] for x in final]
                self._stream.writerow(dict(zip(names, titles)))
                self._stream.writerow(dict(zip(names, types)))

    def stop(self, **kwargs):
        """Close dictwriter and associated file descriptor."""
        super(Csv, self).stop(**kwargs)
        self._stop(**kwargs)

    def _stop(self, **kwargs):
        self._fd.write("\n")
        self.close_fd()
