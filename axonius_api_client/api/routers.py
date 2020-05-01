# -*- coding: utf-8 -*-
"""REST API route definitions."""
from ..tools import join_url


class Router:
    """Simple object store for REST API routes."""

    def __init__(self, object_type, base, version, **routes):
        """Object store for REST API routes.

        Args:
            object_type (:obj:`str`): object type for this set of routes
            base (:obj:`str`): base path for this set of routes
            version (:obj:`int`): api version for this set of routes
            **routes: routes for this object_type
        """
        self._version = version
        self._base = base
        self._object_type = object_type
        self.root = join_url(base, object_type)
        self._routes = ["root"]
        for k, v in routes.items():
            self._routes.append(k)
            setattr(self, k, join_url(self.root, v))

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


class ApiV1:
    """Routes provided by the Axonius REST API version 1."""

    version = 1
    base = "api/V{version}".format(version=version)

    users = Router(
        object_type="users",
        base=base,
        version=version,
        by_id="{id}",
        cached="cached",
        count="count",
        views="views",
        view_by_id="views/saved/{id}",
        labels="labels",
        fields="fields",
        destroy="destroy",
    )

    devices = Router(
        object_type="devices",
        base=base,
        cached="cached",
        version=version,
        by_id="{id}",
        count="count",
        views="views",
        view_by_id="views/saved/{id}",
        labels="labels",
        fields="fields",
        destroy="destroy",
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
        cnxs="{adapter_name_raw}/clients",
        cnxs_uuid="{adapter_name_raw}/clients/{cnx_uuid}",
        file_upload="{adapter_name_raw}/{adapter_node_id}/upload_file",
        # file_download="{name}/{node_id}/download_file",
        config_set="{adapter_name_raw}/config/{adapter_config_name}",
        config_get="{adapter_name_plugin}/config/{adapter_config_name}",
    )

    alerts = Router(object_type="alerts", base=base, version=version)

    system = Router(
        object_type="system",
        base=base,
        version=version,
        instances="instances",
        meta_about="meta/about",
        meta_historical_sizes="meta/historical_sizes",
        settings_lifecycle="settings/lifecycle",
        settings_gui="settings/gui",
        settings_core="settings/core",
        discover_lifecycle="discover/lifecycle",
        discover_start="discover/start",
        discover_stop="discover/stop",
        roles_default="roles/default",
        roles="roles",
        roles_by_uuid="roles/{uuid}",
        roles_labels="roles/labels",
        users="users",
        user="users/{uuid}",
        central_core="central_core",
        central_core_restore="central_core/restore",
    )

    all_objects = [
        users,
        devices,
        actions,
        adapters,
        alerts,
        system,
    ]


API_VERSION = ApiV1
