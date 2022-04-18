# -*- coding: utf-8 -*-
"""API for working with data scopes."""
from typing import Dict, List, Optional, Union

from ...exceptions import ApiError, NotFoundError
from ...parsers.tables import tablize
from ...tools import listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins

MODEL = json_api.data_scopes.DataScope


class DataScopes(ModelMixins):
    """API for working with Data Scopes."""

    def get(self, value: Optional[str] = None) -> Union[MODEL, List[MODEL]]:
        """Pass."""
        self.check_enabled()
        asset_scopes = self.get_asset_scopes()
        response = self._get()
        scopes = response.get_scopes(asset_scopes=asset_scopes)

        if value is not None:
            for scope in scopes:
                if value in [scope.name, scope.uuid]:
                    return scope

            raise NotFoundError(
                tablize(
                    value=[x.to_tablize() for x in scopes],
                    err=f"Data scope with name or UUID of {value!r} not found",
                )
            )
        return scopes

    def create(
        self,
        name: str,
        device_scopes: Optional[List[str]] = None,
        user_scopes: Optional[List[str]] = None,
        description: str = "",
    ):
        """Pass."""
        if not any([device_scopes, user_scopes]):
            raise ApiError("Must supply at least one user or device scope")

        self.check_exists(value=name)

        devices_queries = [
            self.devices.saved_query.get_by_multi(x, as_dataclass=True, asset_scopes=True).uuid
            for x in listify(device_scopes)
        ]
        users_queries = [
            self.users.saved_query.get_by_multi(x, as_dataclass=True, asset_scopes=True).uuid
            for x in listify(user_scopes)
        ]
        self._create(
            name=name,
            devices_queries=devices_queries,
            users_queries=users_queries,
            description=description,
        )
        return self.get(value=name)

    def delete(self, value: str) -> MODEL:
        """Pass."""
        item = self.get(value=value)
        self._delete(uuid=item.uuid)
        return item

    def update_name(self, value: str, update: str) -> MODEL:
        """Pass."""
        item = self.get(value=value)
        self.check_exists(value=update)
        item.name = update
        self._update_from_model(value=item)
        return self.get(value=update)

    def update_description(self, value: str, update: str) -> MODEL:
        """Pass."""
        item = self.get(value=value)
        item.description = update
        self._update_from_model(value=item)
        return self.get(value=value)

    def update_user_scopes(
        self, value: str, update: List[str], append: bool = False, remove: bool = False
    ) -> MODEL:
        """Pass."""
        item = self.get(value=value)
        queries = [
            self.users.saved_query.get_by_multi(x, as_dataclass=True, asset_scopes=True)
            for x in listify(update)
        ]
        query_ids = [x.uuid for x in queries]

        if not queries:
            raise ApiError("Must supply at least one user asset scope")

        if remove:
            item.users_queries = [x for x in item.users_queries if x not in query_ids]
        elif append:
            item.users_queries += [x for x in query_ids if x not in item.users_queries]
        else:
            item.users_queries = query_ids

        self._update_from_model(value=item)
        return self.get(value=value)

    def update_device_scopes(
        self, value: str, update: List[str], append: bool = False, remove: bool = False
    ) -> MODEL:
        """Pass."""
        item = self.get(value=value)
        queries = [
            self.devices.saved_query.get_by_multi(x, as_dataclass=True, asset_scopes=True)
            for x in listify(update)
        ]
        query_ids = [x.uuid for x in queries]

        if not queries:
            raise ApiError("Must supply at least one device asset scope")

        if remove:
            item.devices_queries = [x for x in item.devices_queries if x not in query_ids]
        elif append:
            item.devices_queries += [x for x in query_ids if x not in item.devices_queries]
        else:
            item.devices_queries = query_ids

        self._update_from_model(value=item)
        return self.get(value=value)

    def check_enabled(self):
        """Pass."""
        self.instances.feature_flags.data_scope_check()

    def check_exists(self, value: str):
        """Pass."""
        try:
            existing = self.get(value=value)
        except NotFoundError:
            return
        else:
            raise ApiError(f"Data scope with name of {value!r} already exists:\n{existing}")

    def get_asset_scopes(self) -> Dict[str, List[json_api.saved_queries.SavedQuery]]:
        """Pass."""
        return {
            "devices": [
                x for x in self.devices.saved_query.get(as_dataclass=True) if x.asset_scope
            ],
            "users": [x for x in self.users.saved_query.get(as_dataclass=True) if x.asset_scope],
        }

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from .. import Devices, Users, Instances

        self.devices: Devices = Devices(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.users: Users = Users(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.instances: Instances = Instances(auth=self.auth, **kwargs)
        """API model for cross reference."""

    def _get(self) -> json_api.data_scopes.DataScopeDetails:
        """Direct API method to get all data scopes."""
        api_endpoint = ApiEndpoints.data_scopes.get
        return api_endpoint.perform_request(http=self.auth.http)

    def _delete(self, uuid: str) -> json_api.generic.Metadata:
        """Pass."""
        api_endpoint = ApiEndpoints.data_scopes.delete
        return api_endpoint.perform_request(http=self.auth.http, uuid=uuid)

    def _create(
        self, name: str, devices_queries: List[str], users_queries: List[str], description: str = ""
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
        devices_queries: List[str],
        users_queries: List[str],
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
        """Pass."""
        return self._update(
            uuid=value.uuid,
            name=value.name,
            devices_queries=value.devices_queries,
            users_queries=value.users_queries,
            description=value.description,
        )
