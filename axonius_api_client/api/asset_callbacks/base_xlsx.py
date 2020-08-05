# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from typing import List

import xlsxwriter

from ...exceptions import ApiError
from ...tools import listify
from .base import Base


class Xlsx(Base):
    """Pass."""

    CB_NAME: str = "xlsx"
    CELL_FORMAT: dict = {"text_wrap": True}
    COLUMN_LENGTH: int = 50

    def _init(self, **kwargs):
        """Pass."""
        self.GETARGS["field_null"] = True
        self.GETARGS["field_flatten"] = True
        self.GETARGS["field_join"] = True
        if self.GETARGS.get("field_titles", None) is None:
            self.GETARGS["field_titles"] = True

    def start(self, **kwargs):
        """Create csvstream and associated file descriptor."""
        super(Xlsx, self).start(**kwargs)
        self.do_start(**kwargs)

    def do_start(self, **kwargs):
        """Pass."""
        export_file = self.GETARGS.get("export_file", None)
        if export_file:
            if not str(export_file).endswith(".xlsx"):
                self.GETARGS["export_file"] = f"{export_file}.xlsx"
            self.open_fd_path()
            self._fd.close()
        else:
            msg = "Must supply export_file for this export method"
            self.echo(msg=msg, error=ApiError, level="error")

        self._workbook = xlsxwriter.Workbook(
            str(self._file_path), {"constant_memory": True}
        )
        self._cell_format = self._workbook.add_format(self.CELL_FORMAT)

        worksheet = f"{self.APIOBJ.__class__.__name__}"
        self._worksheet = self._workbook.add_worksheet(worksheet)

        for idx, column_name in enumerate(self.final_columns):
            self._worksheet.write(0, idx, column_name, self._cell_format)
            self._worksheet.set_column(idx, idx, self.COLUMN_LENGTH)
        self._rowtracker = 1

    def stop(self, **kwargs):
        """Close dictwriter and associated file descriptor."""
        super(Xlsx, self).stop(**kwargs)
        self.do_stop(**kwargs)

    def do_stop(self, **kwargs):
        """Pass."""
        self._workbook.close()

    def process_row(self, row: dict) -> List[dict]:
        """Write row to dictwriter and delete it."""
        self.do_pre_row()

        row_return = [{"internal_axon_id": row["internal_axon_id"]}]
        new_rows = self.do_row(row=row)

        for new_row in listify(new_rows):
            for idx, column_name in enumerate(self.final_columns):
                self._worksheet.write(
                    self._rowtracker, idx, new_row.get(column_name), self._cell_format
                )

            self._rowtracker += 1
            del new_row

        del new_rows
        del row

        return row_return
