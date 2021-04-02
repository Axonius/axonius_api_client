# -*- coding: utf-8 -*-
"""API for working with enforcements."""
from typing import List

from ...exceptions import ApiError, NotFoundError
from ...parsers.tables import tablize
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..models import ApiModel


class Actions(ApiModel):
    """API for working with Actions in the Enforcement Center."""

    def get(self) -> List[json_api.actions.Action]:
        """Pass."""
        return self._get()

    def get_by_name(self, value: str) -> json_api.actions.Action:
        """Pass."""
        data = self.get()
        found = [x for x in data if x.name == value]
        if found:
            return found[0]

        err = f"Action with name of {value!r} not found"
        raise NotFoundError(tablize(value=[x.to_tablize() for x in data], err=err))

    # PBUG: title and category of actions stored statically in javascript for GUI
    def get_types(self) -> List[json_api.actions.ActionType]:
        """Pass."""
        return self._get_types()

    def get_type_by_name(self, value: str) -> json_api.actions.ActionType:
        """Pass."""
        data = self.get_types()
        found = [x for x in data if x.name == value]
        if found:
            return found[0]

        err = f"Action Type with name of {value!r} not found"
        raise NotFoundError(tablize(value=[x.to_tablize() for x in data], err=err))

    def _get_types(self) -> List[json_api.actions.ActionType]:
        """Pass."""
        api_endpoint = ApiEndpoints.actions.get_types
        return api_endpoint.perform_request(client=self.CLIENT)

    def _get(self) -> List[json_api.actions.Action]:
        """Pass."""
        api_endpoint = ApiEndpoints.actions.get
        return api_endpoint.perform_request(client=self.CLIENT)

    def _check_name_exists(self, value: str):
        """Pass."""
        try:
            self.get_by_name(value=value)
        except NotFoundError:
            return

        raise ApiError(f"Action with name of {value!r} already exists")
