# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .. import tools
from . import mixins


class Reports(mixins.Child):
    """Child API model that provides special reports for the parent asset type."""

    def missing_adapters(self, rows, adapters=None, fields=None):
        """Report on assets that do not have data from configured adapters.

        Args:
            rows (:obj:`list` of :obj:`dict`): assets to add fields

                * 'missing' - adapters that have a connection and have fetched
                  at least one other asset yet are missing from an asset
                * 'missing_nocnx' - all adapters that do not have a connection and
                  as such are missing from an asset
            adapters (:obj:`dict`, optional): default ``None`` - previously fetched
                metadata for all adapters. will use
                :meth:`.adapters.Adapters.get` if not provided
            fields (:obj:`dict`, optional): default ``None`` - previously fetched
                fields for all adapters. will use :meth:`Fields.get` if not provided

        Returns:
            (:obj:`list` of :obj:`dict`): assets with 'missing' and 'missing_nocnx'
                fields added
        """
        adapters = adapters or self._parent.adapters.get()
        fields = fields or self._parent.fields.get()
        new_rows = []

        for raw_row in rows:
            # row = {k: v for k, v in raw_row.items() if "." in k or k in ["labels"]}
            row = {k: v for k, v in raw_row.items()}
            row["adapters"] = tools.strip_right(
                obj=tools.listify(obj=raw_row.get("adapters", [])), fix="_adapter"
            )
            row["missing_nocnx"] = []
            row["missing"] = []

            for adapter in adapters:
                # this row does not have data from this adapter
                if adapter["name"] not in row["adapters"]:
                    # this adapter has no connections
                    if not adapter["cnx"]:
                        row["missing_nocnx"].append(adapter["name"])
                    # this adapter has been fetched by other assets, but not this one
                    elif adapter["name"] in fields:
                        row["missing"].append(adapter["name"])

            new_rows.append(row)

        return new_rows
