# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""

import tabulate

from ...constants import TABLE_FORMAT, TABLE_MAX_ROWS
from ...exceptions import ApiError
from ...tools import listify
from .base import Base


class Table(Base):
    """Pass."""

    CB_NAME = "table"

    def start(self, **kwargs):
        """Create file descriptor."""
        super(Table, self).start(**kwargs)
        self.GETARGS["field_null"] = True
        self.GETARGS["field_flatten"] = True
        self.GETARGS["field_join"] = True
        self.GETARGS["field_titles"] = True

        self._table_format = self.GETARGS.get("table_format", TABLE_FORMAT)
        self.check_fmt(fmt=self._table_format)
        self._rows = []
        self.open_fd()

    def stop(self, **kwargs):
        """Close file descriptor."""
        super(Table, self).stop(**kwargs)
        rows = getattr(self, "_rows", [])

        table = tabulate.tabulate(
            tabular_data=rows,
            tablefmt=self._table_format,
            showindex=False,
            headers="keys",
        )

        self._fd.write(table)
        self._fd.write("\n")
        self.close_fd()

    def row(self, row):
        """Process row."""
        self.check_stop()
        rows = super(Table, self).row(row=row)
        # XXX textwrap key/values
        self._rows += listify(rows)
        return rows

    def check_stop(self):
        """Pass."""
        max_rows = self.GETARGS.get("table_max_rows", TABLE_MAX_ROWS)
        rows_processed = self.STATE.get("rows_processed", 0)

        if all([rows_processed, max_rows]) and rows_processed >= max_rows:
            self.STATE["stop_fetch"] = True
            self.STATE["stop_msg"] = f"table_max_rows of {max_rows}"

    def check_fmt(self, fmt):
        """Pass."""
        if fmt not in tabulate.tabulate_formats:
            fmts = ", ".join(tabulate.tabulate_formats)
            msg = f"{fmt!r} is not a valid table format, must be one of {fmts}"
            self.echo(msg=msg, error=ApiError)

    @property
    def args_map(self):
        """Pass."""
        args = super(Table, self).args_map
        return args + [
            ["table_format", "Use table format", TABLE_FORMAT],
            ["table_max_rows", "Maximum table rows", TABLE_MAX_ROWS],
        ]
