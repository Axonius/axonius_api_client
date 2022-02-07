# -*- coding: utf-8 -*-
"""Table export callbacks."""
from typing import List, Union

import tabulate

from ...constants.api import TABLE_FORMAT, TABLE_MAX_ROWS
from ...exceptions import ApiError, StopFetch
from ...tools import listify
from .base import ExportMixins


class Table(ExportMixins):
    """Callbacks for formatting asset data and exporting it in text table format.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

        * :meth:`args_map` for callback generic arguments to format assets.
        * :meth:`args_map_custom` for callback specific arguments to format and export data.

    """

    @classmethod
    def args_map_custom(cls) -> dict:
        """Get the custom argument names and their defaults for this callbacks object.

        Examples:
            Export the output to STDOUT. If ``export_file`` is not supplied, the default is to
            print the output to STDOUT.

            >>> assets = apiobj.get(export="table")

            Export the output to a file in the default path
            :attr:`axonius_api_client.setup_env.DEFAULT_PATH`.

            >>> assets = apiobj.get(export="table", export_file="test.txt")

            Export the output to an absolute path file (ignoring ``export_path``) and overwrite
            the file if it exists.

            >>> assets = apiobj.get(
            ...     export="table",
            ...     export_file="/tmp/output.txt",
            ...     export_overwrite=True,
            ... )

            Export the output to a file in a specific dir.

            >>> assets = apiobj.get(export="table", export_file="output.txt", export_path="/tmp")

            Use a different output format.

            >>> assets = apiobj.get(
            ...     export="table",
            ...     export_file="test.txt",
            ...     table_format="mediawiki",
            ... )

            Specify a specific set of rows to return in the output.

            >>> assets = apiobj.get(
            ...     export="table",
            ...     export_file="test.txt",
            ...     table_max_rows=20,
            ... )

            Do not exclude API internal fields from table output.

            >>> assets = apiobj.get(
            ...     export="table",
            ...     export_file="test.txt",
            ...     table_api_fields=True,
            ... )

        See Also:
            * :meth:`args_map` for callback generic arguments to format assets.

        Notes:
            If ``export_file`` is not supplied, the default is to print the output to STDOUT.

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

        table_format = self.get_arg_value("table_format") or TABLE_FORMAT
        self.set_arg_value("table_format", self.check_table_format(fmt=table_format))

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Table, self).start(**kwargs)
        self._rows = []
        self.open_fd()

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        super(Table, self).stop(**kwargs)
        tablefmt = self.get_arg_value("table_format") or TABLE_FORMAT
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
            reason = f"table_max_rows of {max_rows}"
            self.STATE["stop_fetch"] = True
            self.STATE["stop_msg"] = reason
            self.APIOBJ.LOG.info(f"Issuing stop of fetch due to {reason}")
            raise StopFetch(reason=reason, state=self.STATE)

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
        return fmt

    CB_NAME: str = "table"
    """name for this callback"""
