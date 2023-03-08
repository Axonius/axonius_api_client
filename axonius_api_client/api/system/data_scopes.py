# -*- coding: utf-8 -*-
"""API for working with data scopes."""
import typing as t

import cachetools

from ...exceptions import ApiError, NotFoundError
from ...parsers.tables import tablize
from ...tools import listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins

MODEL = json_api.data_scopes.DataScope
SELECT = t.Union[str, MODEL]
MODEL_SQ = json_api.saved_queries.SavedQuery
SELECT_SQ = t.Union[str, MODEL_SQ]
SELECT_SQS = t.Union[SELECT_SQ, t.List[SELECT_SQ]]
CACHE_GET: cachetools.TTLCache = cachetools.TTLCache(maxsize=1024, ttl=60)


class DataScopes(ModelMixins):
    """API for working with Data Scopes."""

    def get(self, value: t.Optional[SELECT] = None) -> t.Union[MODEL, t.List[MODEL]]:
        """Get data scopes.

        Args:
            value (t.Optional[SELECT], optional): Name or UUID of Data Scope to get

        Returns:
            t.Union[MODEL, t.List[MODEL]]: Data scope objects

        Raises:
            NotFoundError: If value supplied and no data scopes match UUID or name
        """
        self.check_feature_enabled()
        response: json_api.data_scopes.DataScopeDetails = self._get()
        scopes: t.List[MODEL] = response.get_scopes()

        if value is not None:
            for scope in scopes:
                if isinstance(value, str) and value in [scope.name, scope.uuid]:
                    return scope
                if isinstance(value, MODEL) and (
                    value.name == scope.name or value.uuid == scope.uuid
                ):
                    return scope

            raise NotFoundError(
                tablize(
                    value=[x.to_tablize() for x in scopes],
                    err=f"Data scope not found with name or UUID of {value!r}",
                )
            )
        return scopes

    def get_cached_single(self, value: t.Union[str, dict, MODEL]) -> MODEL:
        """Pass."""
        name = MODEL._get_attr_value(value=value, attr="name")
        uuid = MODEL._get_attr_value(value=value, attr="uuid")
        items = self.get_cached()
        for item in items:
            if name == item.name or uuid == item.uuid:
                return item

        err = f"No data scope found with name of {name!r} or UUID of {uuid!r}"
        raise NotFoundError(tablize(value=[x.to_tablize() for x in items], err=err))

    @cachetools.cached(cache=CACHE_GET)
    def get_cached(self, safe: bool = False) -> t.List[MODEL]:
        """Get Axonius system users using a cache mechanism."""
        if not self.is_feature_enabled:
            if safe:
                return []
            self.check_feature_enabled()

        response: json_api.data_scopes.DataScopeDetails = self._get()
        scopes: t.List[MODEL] = response.get_scopes()
        return scopes

    def get_safe(self) -> t.List[MODEL]:
        """Get data scopes.

        Notes:
            Used by library to get an empty list object if data scopes feature is not enabled
            on Axonius instance.

        Returns:
            t.List[MODEL]: Data scope objects
        """
        return self.get() if self.is_feature_enabled else []

    def build_role_data_scope(
        self, value: t.Optional[SELECT] = None, required: bool = False
    ) -> dict:
        """Build a data scope restriction dict for use by a system role.

        Args:
            value (t.Optional[SELECT], optional): Name or UUID of data scope
            required (bool, optional): throw error if value is None

        Returns:
            dict: dict for use in 'data_scope_restriction' attribute of a system role

        Raises:
            ApiError: If value is None and required is True
        """
        if value is not None:
            obj = self.get(value=value)
            data_scope = obj.uuid
            enabled = True
        elif required:
            raise ApiError(
                f"Data Scope must be a non-empty string, not type {type(value)} value {value!r}"
            )
        else:
            data_scope = None
            enabled = False

        return json_api.system_roles.build_data_scope_restriction(
            enabled=enabled, data_scope=data_scope
        )

    def create(
        self,
        name: str,
        device_scopes: t.Optional[SELECT_SQS] = None,
        user_scopes: t.Optional[SELECT_SQS] = None,
        description: str = "",
    ) -> MODEL:
        """Create a data scope.

        Args:
            name (str): name
            device_scopes (t.Optional[SELECT_SQS], optional): names/uuids of device asset scopes
            user_scopes (t.Optional[SELECT_SQS], optional): names/uuids of user asset scopes
            description (str, optional): description

        Returns:
            MODEL: Data scope object
        """
        self.check_exists(value=name)

        devices_queries = [
            self.devices.saved_query.get_by_multi(x, as_dataclass=True, asset_scopes=True).uuid
            for x in listify(device_scopes)
        ]
        users_queries = [
            self.users.saved_query.get_by_multi(x, as_dataclass=True, asset_scopes=True).uuid
            for x in listify(user_scopes)
        ]

        if not any([devices_queries, users_queries]):
            raise ApiError("Data Scopes must have a least one user or device Asset Scope")

        self._create(
            name=name,
            devices_queries=devices_queries,
            users_queries=users_queries,
            description=description,
        )
        return self.get(value=name)

    def delete(self, value: SELECT) -> MODEL:
        """Delete a data scope.

        Args:
            value (SELECT): Name or UUID of data scope

        Returns:
            MODEL: Data scope object
        """
        item = self.get(value=value)
        self._delete(uuid=item.uuid)
        return item

    def update_name(self, value: SELECT, update: str) -> MODEL:
        """Update the name of a data scope.

        Args:
            value (SELECT): Name or UUID of data scope
            update (str): New name

        Returns:
            MODEL: Data scope object
        """
        item = self.get(value=value)
        self.check_exists(value=update)
        item.name = update
        self._update_from_model(value=item)
        return self.get(value=update)

    def update_description(self, value: SELECT, update: str) -> MODEL:
        """Update the description of a data scope.

        Args:
            value (SELECT): Name or UUID of data scope
            update (str): New description

        Returns:
            MODEL: Data scope object
        """
        item = self.get(value=value)
        item.description = update
        self._update_from_model(value=item)
        return self.get(value=value)

    def update_user_scopes(
        self,
        value: SELECT,
        update: SELECT_SQS,
        append: bool = False,
        remove: bool = False,
    ) -> MODEL:
        """Update the user asset scopes of a data scope.

        Args:
            value (SELECT): Name or UUID of data scope
            update (SELECT_SQS): list of names or uuid's of user asset scopes
            append (bool, optional): Append supplied asset scopes (instead of overwriting)
            remove (bool, optional): Remove supplied asset scopes (overrides append)

        Returns:
            MODEL: Data scope object
        """
        item = self.get(value=value)
        scopes = [
            self.users.saved_query.get_by_multi(x, as_dataclass=True, asset_scopes=True)
            for x in listify(update)
        ]
        item.update_scopes(scope_type="users", scopes=scopes, append=append, remove=remove)
        self._update_from_model(value=item)
        return self.get(value=value)

    def update_device_scopes(
        self,
        value: SELECT,
        update: SELECT_SQS,
        append: bool = False,
        remove: bool = False,
    ) -> MODEL:
        """Update the device asset scopes of a data scope.

        Args:
            value (SELECT): Name or UUID of data scope
            update (SELECT_SQS): list of names or uuid's of device asset scopes
            append (bool, optional): Append supplied asset scopes (instead of overwriting)
            remove (bool, optional): Remove supplied asset scopes (overrides append)

        Returns:
            MODEL: Data scope object
        """
        item = self.get(value=value)
        scopes = [
            self.devices.saved_query.get_by_multi(x, as_dataclass=True, asset_scopes=True)
            for x in listify(update)
        ]
        item.update_scopes(scope_type="devices", scopes=scopes, append=append, remove=remove)
        self._update_from_model(value=item)
        return self.get(value=value)

    def check_feature_enabled(self):
        """Check if Data Scope feature is enabled for this instance of Axonius."""
        self.instances.feature_flags.data_scope_check()

    @property
    def is_feature_enabled(self) -> bool:
        """Check if Data Scope feature is enabled for this instance of Axonius."""
        return self.instances.feature_flags.data_scopes_enabled

    def check_exists(self, value: str):
        """Check if a data scope exists already."""
        try:
            existing = self.get(value=value)
        except NotFoundError:
            return
        else:
            raise ApiError(f"Data scope with name of {value!r} already exists:\n{existing}")

    # def get_asset_scopes(self) -> t.Dict[str, t.List[json_api.saved_queries.SavedQuery]]:
    #     """Get all saved queries that are asset scopes for each asset type."""
    #     return {
    #         "devices": [
    #             x for x in self.devices.saved_query.get(as_dataclass=True) if x.asset_scope
    #         ],
    #         "users": [x for x in self.users.saved_query.get(as_dataclass=True) if x.asset_scope],
    #     }

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from .. import Devices, Instances, SystemRoles, Users

        self.devices: Devices = Devices(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.users: Users = Users(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.instances: Instances = Instances(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.system_roles: SystemRoles = SystemRoles(auth=self.auth, **kwargs)
        """API model for cross reference."""

    def _get(self) -> json_api.data_scopes.DataScopeDetails:
        """Direct API method to get all data scopes."""
        api_endpoint = ApiEndpoints.data_scopes.get
        return api_endpoint.perform_request(http=self.auth.http)

    def _delete(self, uuid: str) -> json_api.generic.Metadata:
        """Direct API method to delete a data scope by UUID."""
        api_endpoint = ApiEndpoints.data_scopes.delete
        return api_endpoint.perform_request(http=self.auth.http, uuid=uuid)

    def _create(
        self,
        name: str,
        devices_queries: t.List[str],
        users_queries: t.List[str],
        description: str = "",
    ) -> json_api.generic.Metadata:
        """Direct API method to create a data scope."""
        api_endpoint = ApiEndpoints.data_scopes.create
        request_obj = api_endpoint.load_request(
            name=name,
            devices_queries=devices_queries,
            users_queries=users_queries,
            description=description,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _update(
        self,
        uuid: str,
        name: str,
        devices_queries: t.List[str],
        users_queries: t.List[str],
        description: str = "",
    ) -> json_api.generic.Metadata:
        """Direct API method to update a data scope."""
        api_endpoint = ApiEndpoints.data_scopes.update
        request_obj = api_endpoint.load_request(
            uuid=uuid,
            name=name,
            devices_queries=devices_queries,
            users_queries=users_queries,
            description=description,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj, uuid=uuid)

    def _update_from_model(self, value: MODEL) -> json_api.generic.Metadata:
        """Update a data scope from a model object."""
        return self._update(
            uuid=value.uuid,
            name=value.name,
            devices_queries=value.devices_queries,
            users_queries=value.users_queries,
            description=value.description,
        )
