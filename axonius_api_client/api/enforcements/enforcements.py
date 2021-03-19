# -*- coding: utf-8 -*-
"""API for working with enforcements."""
from typing import Generator, List, Optional, Union

from ...constants.api import MAX_PAGE_SIZE
from ...exceptions import NotFoundError
from ...parsers.tables import tablize
from ...tools import listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..models import ApiModel


class Enforcements(ApiModel):
    """API for working with the Enforcement Center."""

    def get(
        self, generator: bool = False
    ) -> Union[Generator[json_api.enforcements.EnforcementDetails, None, None], List[dict]]:
        """Get Enforcements.

        Args:
            generator: return an iterator for objects that will yield rows as they are fetched

        """
        gen = self.get_generator()
        return gen if generator else list(gen)

    def get_generator(
        self,
    ) -> Generator[json_api.enforcements.EnforcementDetails, None, None]:
        """Get Axonius system users using a generator."""
        offset = 0

        while True:
            rows = self._get(offset=offset)
            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row

    def get_names(self) -> List[str]:
        """Pass."""
        data = self._get_names()
        return [x.value for x in data]

    def get_by_name(self, value: str) -> json_api.enforcements.EnforcementDetails:
        """Get an enforcement by name.

        Args:
            value: object name

        Raises:
            :exc:`NotFoundError`: if not found
        """
        data = self.get()
        found = [x for x in data if x.name == value]
        if found:
            return found[0]

        err = f"Enforcement with name of {value!r} not found"
        raise NotFoundError(tablize(value=[x.to_tablize() for x in data], err=err))

    def get_by_uuid(self, value: str) -> json_api.enforcements.EnforcementDetails:
        """Get an enforcement by uuid.

        Raises:
            :exc:`NotFoundError`: if user not found
        """
        data = self.get()
        found = [x for x in data if x.uuid == value]
        if found:
            return found[0]

        err = f"Enforcement with uuid of {value!r} not found"
        raise NotFoundError(tablize(value=[x.to_tablize() for x in data], err=err))

    """

    enforcement.get_by_name/get_by_uuid()
    e_obj = OBJECT
    e_obj.action_main_set(name: str, **config)
    e_obj.action_add(name: str, type: ["post", "success", "failure"], **config)
    e_obj.action_remove(name: str)
    e_obj.trigger_set(asset_type=["users", "devices"], sq="NAME OF SQ", added_only=False)
    e_obj.trigger_configure(enable=True, schedule=[''], only_added=True/False/None,
        only_remove=True/False/None)
    ...
    """

    # def create(self, name: str, action_name: str, action_type: str, action_config: dict):
    #     """Pass."""
    #     enforcements = self.get()
    #     for enforcement in enforcements:
    #         if enforcement.name == name:
    #             raise ApiError(f"Enforcement with name {name!r} already exists:\n{enforcement}")

    #     action_types = self.get_action_types()
    #     found_action_type = None
    #     for action_type in action_types:
    #         if action_type.name == action_type:
    #             found_action_type = action_type

    #     if not found_action_type:
    #         valid = "\n".join([x.name for x in action_types])
    #         msg = f"No action type {action_type!r} found, valid action types:\n{valid}"
    #         raise NotFoundError(msg)

    #     # TODO: parse action config according to found_action.schema

    #     main = {
    #         "name": action_name,
    #         "action": {"action_name": action_type, "config": action_config},
    #     }
    #     return self._create(name=name, main=main)

    def get_actions(self) -> List[json_api.enforcements.Action]:
        """Pass."""
        return self._get_actions()

    def _get_actions(self) -> List[json_api.enforcements.Action]:
        """Pass."""
        api_endpoint = ApiEndpoints.enforcements.get_actions
        return api_endpoint.perform_request(client=self.CLIENT)

    def _create(
        self,
        name: str,
        main: dict,
        success: Optional[List[dict]] = None,
        failure: Optional[List[dict]] = None,
        post: Optional[List[dict]] = None,
        triggers: Optional[List[dict]] = None,
    ) -> str:
        """Create an enforcement set.

        Args:
            name: name of enforcement to create
            main: main action
            success: success actions
            failure: failure actions
            post: post actions
            triggers: saved query trigger
        """
        actions = {
            "main": main,
            "success": success or [],
            "failure": failure or [],
            "post": post or [],
        }
        api_endpoint = ApiEndpoints.enforcements.create
        request_obj = api_endpoint.load_request(name=name, actions=actions, triggers=triggers or [])
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj)

    def _get(
        self, limit: int = MAX_PAGE_SIZE, offset: int = 0
    ) -> List[json_api.enforcements.EnforcementDetails]:
        """Direct API method to get enforcements.

        Args:
            limit: limit to N rows per page
            offset: start at row N
        """
        api_endpoint = ApiEndpoints.enforcements.get
        request_obj = api_endpoint.load_request(page={"limit": limit, "offset": offset})
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj)

    def _get_names(self) -> List[json_api.generic.StrValueSchema]:
        """Pass."""
        api_endpoint = ApiEndpoints.enforcements.get_names
        return api_endpoint.perform_request(client=self.CLIENT)

    def _get_by_uuid(self, uuid: str) -> json_api.enforcements.Enforcement:
        """Pass."""
        api_endpoint = ApiEndpoints.enforcements.get_full
        return api_endpoint.perform_request(client=self.CLIENT, uuid=uuid)

    def _delete(self, uuid: str) -> json_api.generic.Deleted:
        """Pass."""
        ids = listify(uuid)
        api_endpoint = ApiEndpoints.enforcements.delete
        request_obj = api_endpoint.load_request(value={"ids": ids, "include": True})
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj)
