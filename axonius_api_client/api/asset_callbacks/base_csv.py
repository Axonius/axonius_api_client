# -*- coding: utf-8 -*-
"""CSV export callbacks."""
import codecs
import csv
from typing import List, Union

from ...constants.api import FIELD_TRIM_LEN
from ...tools import listify
from .base import ExportMixins


class Csv(ExportMixins):
    """Callbacks for formatting asset data and exporting it in CSV format.

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

            >>> assets = apiobj.get(export="csv")

            Export the output to a file in the default path
            :attr:`axonius_api_client.setup_env.DEFAULT_PATH`.

            >>> assets = apiobj.get(export="csv", export_file="test.csv")

            Export the output to an absolute path file (ignoring ``export_path``) and overwrite
            the file if it exists.

            >>> assets = apiobj.get(
            ...     export="csv",
            ...     export_file="/tmp/output.csv",
            ...     export_overwrite=True,
            ... )

            Export the output to a file in a specific dir.

            >>> assets = apiobj.get(export="csv", export_file="output.csv", export_path="/tmp")

            Include the schema of all selected fields in the output.

            >>> assets = apiobj.get(export="csv", export_schema=True)

            Export the output to a specific file descriptor and do not close the file descriptor
            when finished.

            >>> fd = io.StringIO()
            >>> assets = apiobj.get(export="csv", export_fd=fd, export_fd_close=False)

            Use 'missing' instead of None for rows that are missing a column.

            >>> assets = apiobj.get(export="csv", export_file="test.csv", csv_key_miss='missing')

            Throw an error if an unknown column is found in a row. Must be one of: 'ignore' or
            'raise'.

            >>> assets = apiobj.get(export="csv", export_file="test.csv", csv_key_extras='raise')

            Use 'excel-tab' format instead of 'excel'. Must be one of 'excel', 'excel-tab', or
            'unix'.

            >>> assets = apiobj.get(export="csv", export_file="test.csv", csv_dialect='excel-tab')

            Quote all items instead of just non-numeric. Must be one of 'all', 'minimal',
            'nonnumeric', or 'none'.

            >>> assets = apiobj.get(export="csv", export_file="test.csv", csv_quoting='all')

        See Also:
            * :meth:`args_map` for callback generic arguments to format assets.

        Notes:
            This callbacks object forces the following arguments to True in order to make the
            output usable in the exported format: ``field_null``, ``field_flatten``,
            ``field_join``, ``export_schema``

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
                "field_join_trim": FIELD_TRIM_LEN,
                "export_schema": True,
                "csv_key_miss": None,
                "csv_key_extras": "ignore",
                "csv_dialect": "excel",
                "csv_quoting": "nonnumeric",
            }
        )
        return args

    def _init(self, **kwargs):
        """Override arguments to make export readable."""
        self.set_arg_value("field_null", self.get_arg_value("csv_field_null"))
        self.set_arg_value("field_flatten", self.get_arg_value("csv_field_flatten"))
        self.set_arg_value("field_join", self.get_arg_value("csv_field_join"))

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Csv, self).start(**kwargs)
        self.open_fd()

    def do_start(self, **kwargs):
        """Create the CSV writer and write the columns."""
        if getattr(self, "_stream", None):
            return

        restval = self.get_arg_value("csv_key_miss")

        extras = self.get_arg_value("csv_key_extras")
        # TBD: valid choice check

        dialect = self.get_arg_value("csv_dialect")
        # TBD: valid choice check

        quote = self.get_arg_value("csv_quoting")
        # TBD: valid choice check

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
        export_schema = self.get_arg_value("export_schema")
        field_titles = self.get_arg_value("field_titles")

        if export_schema:
            titles = [x["column_title"] for x in self.final_schemas]
            names = [x["name_qual"] for x in self.final_schemas]
            types = [x["type_norm"] for x in self.final_schemas]
            if field_titles:
                self._stream.writerow(dict(zip(self.final_columns, names)))
                self._stream.writerow(dict(zip(self.final_columns, types)))
            else:
                self._stream.writerow(dict(zip(self.final_columns, titles)))
                self._stream.writerow(dict(zip(self.final_columns, types)))

    CB_NAME: str = "csv"
    """name for this callback"""
