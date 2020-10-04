# -*- coding: utf-8 -*-
"""JSON to CSV export callbacks."""
import json
import tempfile
from typing import List, Union

from ...tools import listify
from .base_csv import Csv


class JsonToCsv(Csv):
    """Callbacks for formatting asset data and exporting it in CSV format using a temp JSON file.

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

            >>> assets = apiobj.get(export="json_to_csv")

            Export the output to a file in the default path
            :attr:`axonius_api_client.setup_env.DEFAULT_PATH`.

            >>> assets = apiobj.get(export="json_to_csv", export_file="test.csv")

            Export the output to an absolute path file (ignoring ``export_path``) and overwrite
            the file if it exists.

            >>> assets = apiobj.get(
            ...     export="json_to_csv",
            ...     export_file="/tmp/output.csv",
            ...     export_overwrite=True,
            ... )

            Export the output to a file in a specific dir.

            >>> assets = apiobj.get(
            ...     export="json_to_csv", export_file="output.csv", export_path="/tmp"
            ... )

            Include the schema of all selected fields in the output.

            >>> assets = apiobj.get(export="json_to_csv", export_schema=True)

            Export the output to a specific file descriptor and do not close the file descriptor
            when finished.

            >>> fd = io.StringIO()
            >>> assets = apiobj.get(export="json_to_csv", export_fd=fd, export_fd_close=False)

            Use 'missing' instead of None for rows that are missing a column.

            >>> assets = apiobj.get(
            ...     export="json_to_csv", export_file="test.csv", csv_key_miss='missing'
            .... )

            Throw an error if an unknown column is found in a row. Must be one of: 'ignore' or
            'raise'.

            >>> assets = apiobj.get(
            ...     export="json_to_csv", export_file="test.csv", csv_key_extras='raise'
            ... )

            Use 'excel-tab' format instead of 'excel'. Must be one of 'excel', 'excel-tab', or
            'unix'.

            >>> assets = apiobj.get(
            ...     export="json_to_csv", export_file="test.csv", csv_dialect='excel-tab'
            ... )

            Quote all items instead of just non-numeric. Must be one of 'all', 'minimal',
            'nonnumeric', or 'none'.

            >>> assets = apiobj.get(
            ...     export="json_to_csv", export_file="test.csv", csv_quoting='all'
            ... )

        See Also:
            * :meth:`args_map` for callback generic arguments to format assets.

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
                "csv_key_miss": None,
                "csv_key_extras": "ignore",
                "csv_dialect": "excel",
                "csv_quoting": "nonnumeric",
            }
        )
        return args

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Csv, self).start(**kwargs)
        self.open_fd()
        self._temp_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        self.echo(msg=f"Writing JSON to temporary file {self._temp_file.name!r}")

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        self.STATE["rows_processed_total"] = 0
        self.do_start(**kwargs)

        self.echo(msg="Re-reading temporary file and converting to CSV")
        self._temp_file.file.seek(0)

        for line in self._temp_file.file.readlines():
            row = json.loads(line.strip())
            rows = listify(row)
            rows = self.do_pre_row(rows=rows)
            rows = self.do_row(rows=rows)
            self.write_rows(rows=rows)
            del rows, row, line

        self.echo(msg=f"Closing and deleting temporary file {self._temp_file.name!r}")
        self._temp_file.file.close()
        super(JsonToCsv, self).stop(**kwargs)

    def process_row(self, row: Union[List[dict], dict]) -> List[dict]:
        """Process the callbacks for current row.

        Args:
            row: row to process
        """
        rows = listify(row)

        row_return = [{"internal_axon_id": row["internal_axon_id"]} for row in rows]
        rows = self.do_pre_row(rows=rows)
        for row in rows:
            value = json.dumps(row)
            self._temp_file.file.write(f"{value}\n")
            del row, value

        return row_return

    CB_NAME: str = "json_to_csv"
    """name for this callback"""
