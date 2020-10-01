# -*- coding: utf-8 -*-
"""Excel export callbacks class."""
from typing import List

import xlsxwriter

from ...exceptions import ApiError
from ...tools import listify
from .base import Base


class Xlsx(Base):
    """Excel export callbacks class.

    See Also:
        See :meth:`args_map` and :meth:`args_map_custom` for details on the extra kwargs that can
        be passed to :meth:`axonius_api_client.api.assets.users.Users.get` or
        :meth:`axonius_api_client.api.assets.devices.Devices.get`
    """

    CB_NAME: str = "xlsx"
    """name for this callback"""

    @classmethod
    def args_map_custom(cls) -> dict:
        """Get the custom argument names and their defaults for this callbacks object.

        See Also:
            :meth:`args_map_export` for the export arguments for this callbacks object.

            :meth:`args_map` for the arguments for all callback objects.

        Notes:
            This callbacks object forces the following arguments to True in order to make the
            output usable in the exported format: ``field_null``, ``field_flatten``,
            and ``field_join``

            These arguments can be supplied as extra kwargs passed to
            :meth:`axonius_api_client.api.assets.users.Users.get` or
            :meth:`axonius_api_client.api.assets.devices.Devices.get`

        """
        args = {}
        args.update(cls.args_map_export())
        args.update(
            {
                "field_titles": True,
                "field_flatten": True,
                "field_join": True,
                "field_null": True,
                "xlsx_column_length": 50,
                "xlsx_cell_format": {"text_wrap": True},
            }
        )
        return args

    def _init(self, **kwargs):
        """Override defaults to make export readable."""
        self.set_arg_value("field_null", True)
        self.set_arg_value("field_flatten", True)
        self.set_arg_value("field_join", True)

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Xlsx, self).start(**kwargs)
        self.do_start(**kwargs)

    def do_start(self, **kwargs):
        """Start this callbacks object."""
        export_file = self.get_arg_value("export_file")
        cell_format = self.get_arg_value("xlsx_cell_format")
        column_length = self.get_arg_value("xlsx_column_length")

        if export_file:
            if not str(export_file).endswith(".xlsx"):
                self.set_arg_value("export_file", f"{export_file}.xlsx")
            self.open_fd_path()
            self._fd.close()
        else:
            msg = "Must supply export_file for this export method"
            self.echo(msg=msg, error=ApiError, level="error")

        self._workbook = xlsxwriter.Workbook(str(self._file_path), {"constant_memory": True})
        self._cell_format = self._workbook.add_format(cell_format)

        worksheet = f"{self.APIOBJ.__class__.__name__}"
        self._worksheet = self._workbook.add_worksheet(worksheet)

        for idx, column_name in enumerate(self.final_columns):
            self._worksheet.write(0, idx, column_name, self._cell_format)
            self._worksheet.set_column(idx, idx, column_length)
        self._rowtracker = 1

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        super(Xlsx, self).stop(**kwargs)
        self.do_stop(**kwargs)

    def do_stop(self, **kwargs):
        """Stop this callbacks object."""
        self._workbook.close()

    def process_row(self, row: dict) -> List[dict]:
        """Write row to dictwriter and delete it."""
        rows = listify(row)
        rows = self.do_pre_row(rows=rows)

        row_return = [{"internal_axon_id": row["internal_axon_id"]} for row in rows]
        rows = self.do_row(rows=rows)

        for row in listify(rows):
            for idx, column_name in enumerate(self.final_columns):
                self._worksheet.write(
                    self._rowtracker, idx, row.get(column_name), self._cell_format
                )

            self._rowtracker += 1
            del row

        del rows

        return row_return
