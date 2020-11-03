# -*- coding: utf-8 -*-
"""XML export callbacks."""
from typing import List, Union

from ...tools import listify
from .base import ExportMixins


class Xml(ExportMixins):
    """Callbacks for formatting asset data and exporting it in XML format.

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

            >>> assets = apiobj.get(export="xml")

            Export the output to a file in the default path
            :attr:`axonius_api_client.setup_env.DEFAULT_PATH`.

            >>> assets = apiobj.get(export="xml", export_file="test.xml")

            Export the output to an absolute path file (ignoring ``export_path``) and overwrite
            the file if it exists.

            >>> assets = apiobj.get(
            ...     export="xml",
            ...     export_file="/tmp/output.txt",
            ...     export_overwrite=True,
            ... )

            Export the output to a file in a specific dir.

            >>> assets = apiobj.get(export="xml", export_file="output.txt", export_path="/tmp")

            Use a different output format.

            >>> assets = apiobj.get(
            ...     export="xml",
            ...     export_file="test.xml",
            ... )

            Specify a specific set of rows to return in the output.

            >>> assets = apiobj.get(
            ...     export="xml",
            ...     export_file="test.xml",
            ... )

            Do not exclude API internal fields from xml output.

            >>> assets = apiobj.get(
            ...     export="xml",
            ...     export_file="test.xml",
            ... )

        See Also:
            * :meth:`args_map` for callback generic arguments to format assets.

        Notes:
            If ``export_file`` is not supplied, the default is to print the output to STDOUT.

            These arguments can be supplied as extra kwargs passed to
            :meth:`axonius_api_client.api.assets.users.Users.get` or
            :meth:`axonius_api_client.api.assets.devices.Devices.get`

        """
        args = {}
        args.update(cls.args_map_export())
        return args

    def _init(self):
        """Override defaults to make export readable."""
        import xmltodict

        self._xmltodict = xmltodict

    def start(self, **kwargs):
        """Start this callbacks object."""
        super(Xml, self).start(**kwargs)
        self._rows = []
        self.open_fd()

    def stop(self, **kwargs):
        """Stop this callbacks object."""
        super(Xml, self).stop(**kwargs)
        rows = getattr(self, "_rows", [])

        asset_type = self.APIOBJ.__class__.__name__.lower()
        xml_obj = {"assets": {asset_type: rows}}
        self._xmltodict.unparse(xml_obj, output=self._fd, pretty=True)
        self.close_fd()

    def process_row(self, row: Union[List[dict], dict]) -> List[dict]:
        """Process the callbacks for current row.

        Args:
            row: row to process
        """
        rows = listify(row)
        rows = self.do_pre_row(rows=rows)
        rows = self.do_row(rows=rows)
        self._rows += rows
        return rows

    CB_NAME: str = "xml"
    """name for this callback"""
