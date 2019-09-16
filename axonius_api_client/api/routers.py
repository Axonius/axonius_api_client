# -*- coding: utf-8 -*-
"""Constants for this package."""
from __future__ import absolute_import, division, print_function, unicode_literals

from .. import tools


class Router(object):
    """Simple object store for REST API routes."""

    def __init__(self, object_type, base, version, **routes):
        """Constructor.

        Args:
            object_type (:obj:`str`):
                Object type.

        """
        self._version = version
        self._base = base
        self._object_type = object_type
        self.root = tools.join_url(base, object_type)
        self._routes = ["root"]
        for k, v in routes.items():
            self._routes.append(k)
            setattr(self, k, tools.join_url(self.root, v))

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        msg = "{obj.__class__.__module__}.{obj.__class__.__name__}"
        msg += "(object_type={obj._object_type!r}, version={obj._version})"
        return msg.format(obj=self)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()


class ApiV1(object):
    """Routes provided by the Axonius REST API version 1."""

    version = 1
    base = "api/V{version}".format(version=version)

    users = Router(
        object_type="users",
        base=base,
        version=version,
        by_id="{id}",
        count="count",
        views="views",
        labels="labels",
        fields="fields",
    )

    devices = Router(
        object_type="devices",
        base=base,
        version=version,
        by_id="{id}",
        count="count",
        views="views",
        labels="labels",
        fields="fields",
    )

    actions = Router(
        object_type="actions",
        base=base,
        version=version,
        shell="shell",  # nosec
        deploy="deploy",
        upload_file="upload_file",
    )

    adapters = Router(
        object_type="adapters",
        base=base,
        version=version,
        cnxs="{adapter_name}/clients",
        cnxs_uuid="{adapter_name}/clients/{cnx_uuid}",
        upload_file="{adapter_name}/{node_id}/upload_file",
    )

    alerts = Router(object_type="alerts", base=base, version=version)

    all_objects = [users, devices, actions, adapters, alerts]
