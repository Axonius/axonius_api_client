# -*- coding: utf-8 -*-
"""API for working with enforcements."""
from typing import Generator, List, Optional, Union

from ...constants.api import MAX_PAGE_SIZE
from ...exceptions import ApiError, NotFoundError
from ...parsers.tables import tablize
from ...tools import listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..models import ApiModel


class Enforcements(ApiModel):
    """API for working with the Enforcement Center."""

    def get(
        self,
        generator: bool = False,
        full: bool = False,
    ) -> Union[
        Generator[
            Union[json_api.enforcements.EnforcementBasic, json_api.enforcements.Enforcement],
            None,
            None,
        ],
        List[dict],
    ]:
        """Get Enforcements.

        Args:
            generator: return an iterator for objects that will yield rows as they are fetched

        """
        gen = self.get_generator(full=full)
        return gen if generator else list(gen)

    def get_generator(
        self,
        full: bool = False,
    ) -> Generator[
        Union[json_api.enforcements.EnforcementBasic, json_api.enforcements.Enforcement],
        None,
        None,
    ]:
        """Get Axonius system users using a generator."""
        offset = 0

        while True:
            rows = self._get(offset=offset)
            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row.get_full() if full else row

    def get_by_name(self, value: str, full: bool = True) -> json_api.enforcements.Enforcement:
        """Get an enforcement by name.

        Args:
            value: object name

        Raises:
            :exc:`NotFoundError`: if not found
        """
        data = self.get()
        found = [x for x in data if x.name == value]
        if found:
            return found[0].get_full() if full else found[0]

        err = f"Enforcement with name of {value!r} not found"
        raise NotFoundError(tablize(value=[x.to_tablize() for x in data], err=err))

    def get_by_uuid(self, value: str, full: bool = True) -> json_api.enforcements.Enforcement:
        """Get an enforcement by uuid.

        Raises:
            :exc:`NotFoundError`: if not found
        """
        data = self.get()
        found = [x for x in data if x.uuid == value]
        if found:
            return found[0].get_full() if full else found[0]

        err = f"Enforcement with uuid of {value!r} not found"
        raise NotFoundError(tablize(value=[x.to_tablize() for x in data], err=err))

    def create(
        self,
        name: str,
        main_action_name: str,
        main_action_type: str,
        trigger_name: Optional[str] = None,  # view.id
        trigger_type: Optional[str] = None,  # view.entity
        only_run_against_new_assets: bool = False,  # run_on
        **kwargs,
    ) -> json_api.enforcements.Enforcement:
        """Create an enforcement set.

        run_only_when_count_above: Optional[int] = None,  # conditions.above
        run_only_when_count_below: Optional[int] = None,  # conditions.below
        run_only_when_count_increases: bool = False,  # conditions.new_entities
        run_only_when_count_decreases: bool = False,  # conditions.previous_entities
        schedule: str = "?",  # period / period_time

        trigger:
            last_triggered: None
            result: "2021-04-01 21:23:03+00:00"
            result_count: 34
            times_triggered: 0
            id: "Trigger"
            name: "Trigger"

            discovery schedule:
                period: "all"
                period_time: "13:00" (UTC) (ignored for this one?)

            days_of_month schedule:
                period: "monthly"
                period_recurrance: ["1", "8", "7", "5", "3", "28", "29"]
                period_time: "13:00" (UTC)

            hourly schedule:
                period: "hourly"
                period_recurrence: 12
                period_time: "13:00" (UTC) (ignored for this one?)

            daily schedule:
                period: "daily"
                period_recurrence: 2 (every 2 days)
                period_time: "13:00" (UTC)

            days of week schedule
                period: "weekly"
                period_recurrence: ["0", "1", "2", "3", "4", "6"] (every day cept sat)
                period_time: "13:00" (UTC)

            period_time is from 00:00 to 23:59, but can be ignored for all and hourly
            period is one of all, monthly, hourly, daily, weekly
            period_recurrence is dependent on period
            schedule_type = ["discovery", "monthly", "hourly", "daily", "weekly"]
            schedule_hour = "13" (00 to 23)
            schedule_minute = "00" (00 to 59)

        Args:
            name: name to assign to the enforcement set
            main_action_name: name to assign to the main action for the enforcement set
            main_action_type: type of action to use for the main action
            **kwargs: configuration values for the main_action_type supplied
        """
        self._check_name_exists(value=name)
        self.CLIENT.actions._check_name_exists(value=main_action_name)
        main_action_type = self.CLIENT.actions.get_type_by_name(value=main_action_type)

        triggers = None
        view = self._find_trigger(name=trigger_name, type=trigger_type)
        if view:
            trigger = {"view": view}
            trigger["run_on"] = self._get_run_on(value=only_run_against_new_assets)
            triggers = [trigger]

        # TODO: parse action config according to found_action.schema
        main = {
            "name": main_action_name,
            "action": {"action_name": main_action_type.name, "config": kwargs},
        }
        return self._create(name=name, main=main, triggers=triggers)

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
    ) -> List[json_api.enforcements.EnforcementBasic]:
        """Direct API method to get enforcements.

        Args:
            limit: limit to N rows per page
            offset: start at row N
        """
        api_endpoint = ApiEndpoints.enforcements.get
        request_obj = api_endpoint.load_request(page={"limit": limit, "offset": offset})
        return api_endpoint.perform_request(client=self.CLIENT, request_obj=request_obj)

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

    def _check_name_exists(self, value: str):
        """Pass."""
        try:
            existing = self.get_by_name(value=value)
        except NotFoundError:
            return

        raise ApiError(f"Enforcement with name of {value!r} already exists:\n{existing}")

    @property
    def _triggers_map(self) -> dict:
        """Pass."""
        return {"devices": self.CLIENT.devices, "users": self.client.users}

    def _find_trigger(
        self, name: Optional[str] = None, type: Optional[str] = None
    ) -> Optional[dict]:
        """Pass."""
        if not name:
            return None

        if type not in self._triggers_map:
            valid = ", ".join(list(self._triggers_map))
            raise ApiError(f"Trigger type of {type!r} is not a valid type, valid types: {valid}")

        apiobj = self._triggers_map[type]
        sq = apiobj.saved_query.get_by_name(value=name)
        return {"id": sq["id"], "entity": type}

    def _get_run_on(self, value: bool = False) -> str:
        """Pass."""
        return "AddedEntities" if value else "AllEntities"
