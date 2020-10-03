# -*- coding: utf-8 -*-
"""Table export callbacks class."""
from typing import List, Union

import tabulate

from ...constants.api import TABLE_FORMAT, TABLE_MAX_ROWS
from ...exceptions import ApiError
from ...tools import listify
from .base import Base


class Table(Base):
    """Table export callbacks class.

    See Also:
        See :meth:`args_map` and :meth:`args_map_custom` for details on the extra kwargs that can
        be passed to :meth:`axonius_api_client.api.assets.users.Users.get` or
        :meth:`axonius_api_client.api.assets.devices.Devices.get`

    """

    CB_NAME: str = "table"
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
                "table_format": TABLE_FORMAT,
                "table_max_rows": TABLE_MAX_ROWS,
                "table_api_fields": False,
            }
        )
        return args

    def _init(self):
        """Override defaults to make export readable."""
        self.set_arg_value("field_null", True)
        self.set_arg_value("field_flatten", True)
        self.set_arg_value("field_join", True)

        table_api_fields = self.get_arg_value("table_api_fields")
        if not table_api_fields:
            field_excludes = listify(self.get_arg_value("field_excludes"))
            self.set_arg_value("field_excludes", field_excludes + self.APIOBJ.FIELDS_API)

        table_format = self.get_arg_value("table_format")
        self.set_arg_value("table_format", self.check_table_format(fmt=table_format))

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Table, self).start(**kwargs)
        self._rows = []
        self.open_fd()

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        super(Table, self).stop(**kwargs)
        tablefmt = self.get_arg_value("table_format")
        rows = getattr(self, "_rows", [])

        table = tabulate.tabulate(
            tabular_data=rows,
            tablefmt=tablefmt,
            showindex=False,
            headers="keys",
        )

        self._fd.write(table)
        self._fd.write("\n")
        self.close_fd()

    def process_row(self, row: Union[List[dict], dict]) -> List[dict]:
        """Process the callbacks for current row.

        Args:
            row: row to process
        """
        rows = listify(row)
        rows = self.do_pre_row(rows=rows)
        self.check_stop()
        rows = self.do_row(rows=rows)
        # TBD textwrap key/values
        self._rows += rows
        return rows

    def check_stop(self):
        """Check if rows processed is greater than table_max_rows."""
        max_rows = self.get_arg_value("table_max_rows")
        rows_processed = self.STATE.get("rows_processed_total", 0)

        if all([rows_processed, max_rows]) and rows_processed >= max_rows:
            self.STATE["stop_fetch"] = True
            self.STATE["stop_msg"] = f"table_max_rows of {max_rows}"

    def check_table_format(self, fmt: str):
        """Check if table_format is valid choice.

        Args:
            fmt: table format to check

        Raises:
            :exc:`axonius_api_client.exceptions.ApiError`: if fmt is not a valid choice
        """
        if fmt not in tabulate.tabulate_formats:
            fmts = ", ".join(tabulate.tabulate_formats)
            msg = f"{fmt!r} is not a valid table format, must be one of {fmts}"
            self.echo(msg=msg, error=ApiError)
