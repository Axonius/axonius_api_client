# -*- coding: utf-8 -*-
"""API for working with enforcements."""
from typing import List, Optional

from ...constants.api import MAX_PAGE_SIZE
from ...exceptions import ApiError, NotFoundError
from ...parsers.tables import tablize_notfound
from ...tools import listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..models import ApiModel


class EnforcementCenter(ApiModel):
    """API for working with objects in the Enforcement Center."""

    def get_sets(
        self, generator: bool = False, full: bool = False
    ) -> json_api.enforcement_center.SET_UNION:
        """Get all Enforcement Sets.

        Args:
            generator: return an iterator for objects that will yield rows as they are fetched
            full: return the basic or full objects

        """
        gen = self._get_sets_gen(full=full)
        return gen if generator else list(gen)

    def get_actions(self) -> json_api.enforcement_center.ACTIONS:
        """Get all Actions that are saved in all Enforcement Sets."""
        return self._get_actions()

    def get_action_types(self) -> json_api.enforcement_center.ACTION_TYPES:
        """Get all Action Types that can be used when adding an Action to an Enforcement Set."""
        return self._get_action_types()

    def find_set(self, value: str, full: bool = True) -> json_api.enforcement_center.SET_BOTH:
        """Get an Enforcement Set by name or uuid.

        Args:
            value: object name or uuid
            full: return the basic or full object

        Raises:
            :exc:`NotFoundError`: if not found
        """
        data = self.get_sets(generator=True, full=False)
        found = []
        for item in data:
            found.append(item)
            if value in [item.name, item.uuid]:
                return item.get_full() if full else item

        err = f"Enforcement Set with Name or UUID of {value!r} not found"
        tablize_notfound(found=found, err=err)

    def find_action(self, value: str) -> json_api.enforcement_center.ACTION:
        """Get an Action by name that is saved in any Enforcement Sets.

        Args:
            value: object name

        Raises:
            :exc:`NotFoundError`: if not found
        """
        data = self.get_actions()
        found = []
        for item in data:
            found.append(item)
            if value in [item.name]:
                return item

        err = f"Enforcement Action with name of {value!r} not found"
        tablize_notfound(found=found, err=err)

    def find_action_type(self, value: str) -> json_api.enforcement_center.ACTION_TYPE:
        """Get an Action Type by name that can be used when adding an Action to an Enforcement Set.

        Args:
            value: object name

        Raises:
            :exc:`NotFoundError`: if not found
        """
        data = self.get_action_types()
        found = []
        for item in data:
            found.append(item)
            if value in [item.name]:
                return item

        err = f"Action Type with name of {value!r} not found"
        tablize_notfound(found=found, err=err)

    def create_set(
        self, name: str, action_name: str, action_type: str, **kwargs
    ) -> json_api.enforcement_center.SET_FULL:
        """Create an Enforcement Set.

        Args:
            name: name to assign to the Enforcement Set
            action_name: name to assign to the main action for the Enforcement Set
            action_type: type of action to use for the main action
            **kwargs: configuration values for the action_type supplied


        Raises:
            :exc:`ApiError`: If an Enforcement Set or Action exists with the provided names

        """
        self._check_set_exists(value=name)
        self._check_action_exists(value=action_name)
        atype = self.find_action_type(value=action_type)
        aconfig = kwargs
        main = {"name": action_name, "action": {"action_name": atype.name, "config": aconfig}}
        new_obj = self._create_set(name=name, main=main)
        return self.find_set(value=new_obj.uuid, full=True)

    def _create_set(
        self,
        name: str,
        main: dict,
        success: Optional[List[dict]] = None,
        failure: Optional[List[dict]] = None,
        post: Optional[List[dict]] = None,
        triggers: Optional[List[dict]] = None,
    ) -> json_api.enforcement_center.SET_FULL:
        """Direct API method to create an Enforcement Set.

        Args:
            name: name of Enforcement Set
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
        api_endpoint = ApiEndpoints.enforcement_center.create_set
        request_obj = api_endpoint.load_request(name=name, actions=actions, triggers=triggers or [])
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj)

    def _set_has_running_task(self, name: str) -> json_api.generic.BoolValue:
        """Direct API method to see if an Enforcement Set has a currently running task.

        Args:
            name: name of Enforcement Set
        """
        api_endpoint = ApiEndpoints.enforcement_center.set_has_running_task
        return api_endpoint.perform_request(client=self.CLIENT, name=name)

    def _run_set(
        self, uuid: str, use_conditions: bool = False, ec_page_run: bool = False
    ) -> json_api.generic.NameValue:
        """Direct API method to run an Enforcement Set.

        Args:
            uuid: uuid of Enforcement Set
            use_conditions: only run the Enforcement Set if the Enforcement Sets conditions are met
            ec_page_run: ??? XXX

        """
        api_endpoint = ApiEndpoints.enforcement_center.run_set
        request_obj = api_endpoint.load_request(
            use_conditions=use_conditions, ec_page_run=ec_page_run
        )
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj, uuid=uuid)

    def _update_set(
        self, uuid: str, name: str, actions: dict, triggers: Optional[List[dict]] = None
    ) -> json_api.enforcement_center.SET_FULL:
        """Direct API method to update an Enforcement Set.

        Args:
            uuid: uuid of Enforcement Set
            name: name of Enforcement Set
            actions: actions to update
            triggers: triggers to update

        """
        api_endpoint = ApiEndpoints.enforcement_center.update_set
        request_obj = api_endpoint.load_request(
            id=uuid, uuid=uuid, name=name, actions=actions, triggers=triggers or []
        )
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj, uuid=uuid)

    def _delete_set(self, uuid: str) -> json_api.generic.Deleted:
        """Direct API method to delete an Enforcement Set.

        Args:
            uuid: uuid of Enforcement Set

        """
        ids = listify(uuid)
        api_endpoint = ApiEndpoints.enforcement_center.delete_set
        request_obj = api_endpoint.load_request(value={"ids": ids, "include": True})
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj)

    def _get_sets(
        self, limit: int = MAX_PAGE_SIZE, offset: int = 0
    ) -> json_api.enforcement_center.SETS_BASIC:
        """Direct API method to get all Enforcement Sets in 'basic' format.

        Args:
            limit: limit to N rows per page
            offset: start at row N
        """
        api_endpoint = ApiEndpoints.enforcement_center.get_sets
        request_obj = api_endpoint.load_request(page={"limit": limit, "offset": offset})
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj)

    def _get_sets_gen(self, full: bool = False) -> json_api.enforcement_center.SET_GEN:
        """Get all Enforcement Sets using a generator.

        Args:
            full: return the basic or full objects

        """
        offset = 0

        while True:
            rows = self._get_sets(offset=offset)
            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row.get_full() if full else row

    def _get_set_by_uuid(self, uuid: str) -> json_api.enforcement_center.SET_FULL:
        """Direct API method to get an Enforcement Set in 'full' format.

        Args:
            uuid: uuid of Enforcement Set

        """
        api_endpoint = ApiEndpoints.enforcement_center.get_set_by_uuid
        return api_endpoint.perform_request(client=self.CLIENT, uuid=uuid)

    def _get_action_types(self) -> json_api.enforcement_center.ACTION_TYPES:
        """Direct API method to get all Action Types."""
        api_endpoint = ApiEndpoints.enforcement_center.get_action_types
        return api_endpoint.perform_request(client=self.CLIENT)

    def _get_actions(self) -> json_api.enforcement_center.ACTIONS:
        """Direct API method to get all Saved Actions."""
        api_endpoint = ApiEndpoints.enforcement_center.get_actions
        return api_endpoint.perform_request(client=self.CLIENT)

    def _get_tasks(
        self, uuid: str, limit: int = MAX_PAGE_SIZE, offset: int = 0
    ) -> json_api.enforcement_center.TASKS_BASIC:
        """Direct API method to all tasks for an Enforcement Set in 'basic' format.

        Args:
            uuid: uuid of Enforcement Set to get tasks for
            limit: limit to N rows per page
            offset: start at row N
        """
        api_endpoint = ApiEndpoints.tasks.get_tasks
        request_obj = api_endpoint.load_request(page={"limit": limit, "offset": offset})
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj, uuid=uuid)

    def _get_tasks_gen(self, uuid: str, full: bool = True) -> json_api.enforcement_center.TASK_GEN:
        """Get tasks for an Enforcement Set.

        Args:
            uuid: uuid of Enforcement Set to get tasks for
            full: return the basic or full objects
        """
        offset = 0

        while True:
            rows = self._get(uuid=uuid, offset=offset)
            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row.get_full() if full else row

    def _get_task_by_uuid(self, uuid: str) -> json_api.enforcement_center.TASK_FULL:
        """Direct API method to a task for an Enforcement Set in 'full' format.

        Args:
            uuid: uuid of task
        """
        api_endpoint = ApiEndpoints.enforcement_center.get_task_by_uuid
        return api_endpoint.perform_request(client=self.CLIENT, uuid=uuid)

    def _check_action_exists(self, value: str):
        """Throw an error if an action with a given name exists in any Enforcement Set.

        Args:
            value: name of action
        """
        try:
            self.find_action(value=value)
        except NotFoundError:
            return

        raise ApiError(f"Action with name of {value!r} already exists")

    def _check_set_exists(self, value: str):
        """Throw an error if an Enforcement Set with a given name or uuid exists.

        Args:
            value: name or uuid of Enforcement Set

        Raises:
            :exc:`ApiError`: If an Enforcement Set exists with the provided name or uuid
        """
        try:
            existing = self.find_set(value=value)
        except NotFoundError:
            return

        raise ApiError(f"Enforcement Set with name of {value!r} already exists:\n{existing}")
