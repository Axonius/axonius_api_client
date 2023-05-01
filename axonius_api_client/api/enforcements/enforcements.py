# -*- coding: utf-8 -*-
"""API for working with enforcements."""
import typing as t
import warnings

from cachetools import TTLCache, cached

from ...constants.api import MAX_PAGE_SIZE
from ...exceptions import AlreadyExists, ApiError, ApiWarning, NotAllowedError, NotFoundError
from ...parsers.tables import tablize
from ...tools import listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..folders import FoldersEnforcements
from ..json_api.enforcements import (
    ActionCategory,
    ActionType,
    CreateEnforcementModel,
    EnforcementBasicModel,
    EnforcementDefaults,
    EnforcementFullModel,
    EnforcementSchedule,
    MoveEnforcementsRequestModel,
    MoveEnforcementsResponseModel,
    UpdateEnforcementResponseModel,
)
from ..json_api.folders.base import FolderDefaults
from ..json_api.folders.enforcements import Folder, FolderModel, FoldersModel
from ..json_api.saved_queries import QueryTypes, SavedQuery
from ..mixins import ModelMixins
from .tasks import Tasks

MULTI_SQ = t.Union[str, dict, SavedQuery]
MULTI_SET = t.Union[
    str, dict, EnforcementBasicModel, EnforcementFullModel, UpdateEnforcementResponseModel
]
MULTI_ACTION_TYPE = t.Union[str, dict, ActionType]
CACHE_GET = TTLCache(maxsize=1024, ttl=60)


class Enforcements(ModelMixins):
    """API working with enforcements.

    What's the deal with BASIC vs FULL?

    The REST API exposes an endpoint to page through the enforcement sets,
    but the details about the actions and triggers configured are limited.

    In order to get the full details of the actions and triggers, one call
    must be made to fetch the FULL details of each enforcement set by UUID.

    To make things more fun, the FULL model is lacking details that are
    only provided by the BASIC model:
    triggers_last_triggered, triggers_times_triggered, updated_by, last_triggered,
    last_updated.

    Finally, the "human friendly" description of trigger schedule is only available from BASIC.

    We overcome this by getting the FULL object and attaching the BASIC object as FULL.BASIC.
    """

    @property
    def folders(self) -> FoldersEnforcements:
        """Get the folders api for this object type."""
        # noinspection PyUnresolvedReferences
        return self.auth.http.CLIENT.folders.enforcements

    def get_set(
        self,
        value: MULTI_SET,
        refetch: bool = True,
        cache: t.Optional[t.List[EnforcementFullModel]] = None,
    ) -> EnforcementFullModel:
        """Get an enforcement set by name or UUID.

        Args:
            value: enforcement set model or str with name or uuid
            refetch: refetch the enforcement set from the API
            cache: cache of enforcement sets

        Raises:
            ApiError: if invalid type supplied for value
            NotFoundError: if not found

        Returns:
            EnforcementFullModel: enforcement set model
        """
        if isinstance(value, str):
            name = value
            uuid = value
        elif isinstance(
            value,
            (EnforcementBasicModel, EnforcementFullModel, UpdateEnforcementResponseModel),
        ):
            if not refetch and isinstance(value, EnforcementFullModel):
                return value
            name = value.name
            uuid = value.uuid
        elif isinstance(value, dict) and value.get("name") and value.get("uuid"):
            name = value["name"]
            uuid = value["uuid"]
        else:
            raise ApiError(f"Unknown type {type(value)}, must be {MULTI_SET}")

        items = []
        if (
            isinstance(cache, list)
            and cache
            and all(
                [
                    isinstance(
                        x,
                        (
                            EnforcementBasicModel,
                            EnforcementFullModel,
                            UpdateEnforcementResponseModel,
                        ),
                    )
                    for x in cache
                ]
            )
        ):
            data = cache
        else:
            data = self.get_sets_generator(full=True)

        for item in data:
            if name == item.name or uuid == item.uuid:
                return item
            items.append(item)

        raise NotFoundError(
            tablize(
                value=[x.to_tablize() for x in items],
                err=f"Enforcement Set with name of {name!r} or UUID of {uuid!r} not found",
            )
        )

    @cached(cache=CACHE_GET)
    def get_sets_cached(
        self, **kwargs
    ) -> t.List[t.Union[EnforcementBasicModel, EnforcementFullModel]]:
        """Get all enforcements cached."""
        return list(self.get_sets_generator(**kwargs))

    def get_sets(
        self, generator: bool = False, full: bool = True
    ) -> t.Union[
        t.Generator[t.Union[EnforcementBasicModel, EnforcementFullModel], None, None],
        t.List[t.Union[EnforcementBasicModel, EnforcementFullModel]],
    ]:
        """Get all enforcement sets.

        Args:
            generator: return an iterator for objects
            full: get the full model of each enforcement set
        """
        gen = self.get_sets_generator(full=full)
        return gen if generator else list(gen)

    def get_sets_generator(
        self, full: bool = True
    ) -> t.Generator[t.Union[EnforcementBasicModel, EnforcementFullModel], None, None]:
        """Get all enforcement sets using a generator.

        Args:
            full: get the full model of each enforcement set

        Yields:
            t.Generator[t.Union[EnforcementBasicModel, EnforcementFullModel], None, None]: Generator
        """
        offset = 0

        while True:
            rows = self._get_sets(offset=offset)
            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row.get_full() if full else row

    def check_set_exists(self, value: MULTI_SET):
        """Check if an enforcement set already exists.

        Args:
            value: enforcement set model or str with name or uuid


        Raises:
            ApiError: if enforcement set already exists
        """
        try:
            existing = self.get_set(value=value)
        except NotFoundError:
            return

        exc = AlreadyExists(f"enforcement set matching {value!r} already exists:\n{existing}")
        exc.obj = existing
        raise exc

    def get_action_type(self, value: MULTI_ACTION_TYPE) -> ActionType:
        """Get an action type.

        Args:
            value: action type model or str with name

        Returns:
            ActionType: action type model

        Raises:
            ApiError: if value is incorrect type
            NotFoundError: if not found
        """
        if isinstance(value, str):
            name = value
        elif isinstance(value, dict) and value.get("id"):
            name = value["id"]
        elif isinstance(value, ActionType):
            name = value.name
        else:
            raise ApiError(f"Unknown type {type(value)}, must be str, dict, or {ActionType}")

        items = self.get_action_types()

        for item in items:
            if item.name == name:
                return item

        raise NotFoundError(
            tablize(
                value=[x.to_tablize() for x in items],
                err=f"Action Type with name of {name!r} not found",
            )
        )

    def get_action_types(self) -> t.List[ActionType]:
        """Get all action types.

        Returns:
            t.List[ActionType]: action type models
        """
        return self._get_action_types()

    def copy(
        self,
        value: MULTI_SET,
        name: str,
        copy_triggers: bool = True,
        folder: t.Optional[t.Union[str, Folder]] = None,
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo_action,
    ) -> EnforcementFullModel:
        """Copy an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid
            name: name to assign to copy
            copy_triggers: copy triggers to new set
            folder: folder to put object in
            create: if folder supplied does not exist, create it
            echo: echo output to console during create/etc

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)

        root: FoldersModel = self.folders.get()
        folder: FolderModel = root.resolve_folder(folder=folder, create=create, echo=echo)

        created = self._copy(uuid=existing.uuid, name=name, clone_triggers=copy_triggers)

        # NEAT: can not move to/from public /private in enforcements
        if folder.depth > 1 and folder.id != created.folder.id:
            self._move_sets(folder_id=folder.id, enforcements_ids=created.uuid)

        return self.get_set(value=created)

    def update_folder(
        self,
        value: MULTI_SET,
        folder: t.Union[str, FolderModel],
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo_action,
    ) -> EnforcementFullModel:
        """Update the name of an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid
            folder: folder to put object in
            create: if folder supplied does not exist, create it
            echo: echo output to console during create/etc

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing: EnforcementFullModel = self.get_set(value=value)
        updated_obj: EnforcementFullModel = existing.move(
            folder=folder,
            create=create,
            echo=echo,
            refresh=False,
        )
        return updated_obj

    def update_name(self, value: MULTI_SET, name: str) -> EnforcementFullModel:
        """Update the name of an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid
            name: name to update

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        self.check_set_exists(value=name)
        existing.name = name
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_description(
        self, value: MULTI_SET, description: str, append: bool = False
    ) -> EnforcementFullModel:
        """Update the description of an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid
            description: description to update
            append: append to existing description

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.update_description(value=description, append=append)
        return self.get_set(value=existing)

    def update_action_main(
        self, value: MULTI_SET, name: str, action_type: str, config: t.Optional[dict] = None
    ) -> EnforcementFullModel:
        """Update the main action of an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid
            name: name to assign to action
            action_type: action type
            config: action configuration

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        action = self.get_set_action(name=name, action_type=action_type, config=config)
        existing.main_action = action
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_action_add(
        self,
        value: MULTI_SET,
        category: t.Union[ActionCategory, str],
        name: str,
        action_type: str,
        config: t.Optional[dict] = None,
    ) -> EnforcementFullModel:
        """Add an action to an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid
            category: action category to add action to
            name: name of action to add
            action_type: action type
            config: action configuration

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        action = self.get_set_action(name=name, action_type=action_type, config=config)
        existing.add_action(category=category, action=action)
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_action_remove(
        self, value: MULTI_SET, category: t.Union[ActionCategory, str], name: str
    ) -> EnforcementFullModel:
        """Remove an action from an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid
            category: action category to remove action from
            name: name of action to remove

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.remove_action(category=category, name=name)
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_query(
        self,
        value: MULTI_SET,
        query_name: str,
        query_type: t.Union[QueryTypes, str] = EnforcementDefaults.query_type,
    ) -> EnforcementFullModel:
        """Update the query of an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid
            query_name: name of saved query
            query_type: type of saved query

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        sq = self.get_trigger_view(query_name=query_name, query_type=query_type)
        existing = self.get_set(value=value)
        existing.query_update(query_uuid=sq.uuid, query_type=query_type)
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_query_remove(self, value: MULTI_SET) -> EnforcementFullModel:
        """Remove the query from an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        raise NotAllowedError("Enforcement Sets now require a Saved Query to be defined")

    def update_schedule_never(self, value: MULTI_SET) -> EnforcementFullModel:
        """Set the schedule of an enforcement set to never run.

        Args:
            value: enforcement set model or str with name or uuid

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.set_schedule_never()
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_schedule_discovery(self, value: MULTI_SET) -> EnforcementFullModel:
        """Set the schedule of an enforcement set to run every discovery.

        Args:
            value: enforcement set model or str with name or uuid

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.set_schedule_discovery()
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_schedule_hourly(self, value: MULTI_SET, recurrence: int) -> EnforcementFullModel:
        """Set the schedule of an enforcement set to run hourly.

        Args:
            value: enforcement set model or str with name or uuid
            recurrence: run schedule every N hours (N = 1-24)

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.set_schedule_hourly(recurrence=recurrence)
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_schedule_daily(
        self,
        value: MULTI_SET,
        recurrence: int,
        hour: int = EnforcementDefaults.schedule_hour,
        minute: int = EnforcementDefaults.schedule_minute,
    ) -> EnforcementFullModel:
        """Set the schedule of an enforcement set to run daily.

        Args:
            value: enforcement set model or str with name or uuid
            recurrence: run enforcement every N days (N = 1-~)
            hour: hour of day to run schedule
            minute: minute of hour to run schedule

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.set_schedule_daily(recurrence=recurrence, hour=hour, minute=minute)
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_schedule_weekly(
        self,
        value: MULTI_SET,
        recurrence: t.Union[str, t.List[t.Union[str, int]]],
        hour: int = EnforcementDefaults.schedule_hour,
        minute: int = EnforcementDefaults.schedule_minute,
    ) -> EnforcementFullModel:
        """Set the schedule of an enforcement set to run weekly.

        Args:
            value: enforcement set model or str with name or uuid
            recurrence: run enforcement on days of week
            hour: hour of day to run schedule
            minute: minute of hour to run schedule

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.set_schedule_weekly(recurrence=recurrence, hour=hour, minute=minute)
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_schedule_monthly(
        self,
        value: MULTI_SET,
        recurrence: t.Union[str, t.List[t.Union[int, str]]],
        hour: int = EnforcementDefaults.schedule_hour,
        minute: int = EnforcementDefaults.schedule_minute,
    ) -> EnforcementFullModel:
        """Set the schedule of an enforcement set to run monthly.

        Args:
            value: enforcement set model or str with name or uuid
            recurrence: run enforcement on days of month
            hour: hour of day to run schedule
            minute: minute of hour to run schedule

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.set_schedule_monthly(recurrence=recurrence, hour=hour, minute=minute)
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_only_new_assets(self, value: MULTI_SET, update: bool) -> EnforcementFullModel:
        """Update enforcement set to only run against newly added assets from last automated run.

        Args:
            value: enforcement set model or str with name or uuid
            update: False=run against all assets each automated run, True=only run against
                newly added assets from last automated run

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.only_new_assets = update
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_on_count_increased(self, value: MULTI_SET, update: bool) -> EnforcementFullModel:
        """Update enforcement set to only run if asset count increased from last automated run.

        Args:
            value: enforcement set model or str with name or uuid
            update: False=run regardless if asset count increased, True=only perform
                automated run if asset count increased

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.on_count_increased = update
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_on_count_decreased(self, value: MULTI_SET, update: bool) -> EnforcementFullModel:
        """Update enforcement set to only run if asset count decreased from last automated run.

        Args:
            value: enforcement set model or str with name or uuid
            update: False=run regardless if asset count decreased, True=only perform
                automated run if asset count decreased

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.on_count_decreased = update
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_on_count_above(
        self, value: MULTI_SET, update: t.Optional[int]
    ) -> EnforcementFullModel:
        """Update enforcement set to only run automatically if asset count is above N.

        Args:
            value: enforcement set model or str with name or uuid
            update: None to always run automatically regardless of asset count,
                integer to only run automatically if asset count is above N

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.on_count_above = update
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_on_count_below(
        self, value: MULTI_SET, update: t.Optional[int]
    ) -> EnforcementFullModel:
        """Update enforcement set to only run automatically if asset count is below N.

        Args:
            value: enforcement set model or str with name or uuid
            update: None to always run automatically regardless of asset count,
                integer to only run automatically if asset count is below N

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        existing = self.get_set(value=value)
        existing.on_count_below = update
        updated = self.update_from_model(value=existing)
        return self.get_set(value=updated)

    def update_from_model(self, value: EnforcementFullModel) -> EnforcementFullModel:
        """Update an enforcement set from the values in a model.

        Args:
            value: enforcement set model to update

        Returns:
            EnforcementFullModel: updated enforcement set
        """
        return self._update(
            uuid=value.uuid,
            name=value.name,
            actions=value.actions,
            triggers=value.triggers,
            folder_id=value.folder_id,
        )

    # noinspection PyDefaultArgument
    def create(
        self,
        name: str,
        main_action_name: str,
        main_action_type: str,
        query_name: t.Optional[str] = EnforcementDefaults.query_name,
        query_type: str = EnforcementDefaults.query_type,
        main_action_config: t.Optional[dict] = None,
        description: t.Optional[str] = "",
        schedule_type: t.Union[EnforcementSchedule, str] = EnforcementDefaults.schedule_type,
        schedule_hour: int = EnforcementDefaults.schedule_hour,
        schedule_minute: int = EnforcementDefaults.schedule_minute,
        schedule_recurrence: t.Optional[
            t.Union[int, t.List[str]]
        ] = EnforcementDefaults.schedule_recurrence,
        only_new_assets: bool = EnforcementDefaults.only_new_assets,
        on_count_above: t.Optional[int] = EnforcementDefaults.on_count_above,
        on_count_below: t.Optional[int] = EnforcementDefaults.on_count_below,
        on_count_increased: bool = EnforcementDefaults.on_count_increased,
        on_count_decreased: bool = EnforcementDefaults.on_count_decreased,
        folder: t.Optional[t.Union[str, FolderModel]] = None,
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo_action,
    ) -> EnforcementFullModel:
        """Create an enforcement set.

        Args:
            name: Name to assign to enforcement set
            description: Description to assign to enforcement set
            query_name: Saved Query name to use for trigger
            query_type: Saved Query type
            main_action_name: name to assign to main action
            main_action_type: action type to use for main action
            main_action_config: action config for main action
            schedule_type: EnforcementSchedule type
                for automation
            schedule_hour: Hour of day to use for schedule_type
            schedule_minute: Minute of hour to use for schedule_type
            schedule_recurrence: recurrence value to use for schedule_type
            only_new_assets: only run set against assets added since last run
            on_count_above: only run if asset count above N
            on_count_below: only run if asset count below N
            on_count_increased: only run if asset count increased since last run
            on_count_decreased: only run if asset count decreased since last run
            folder: folder to create set in
            create: create folder if it doesn't exist
            echo: echo folder creation

        Returns:
            EnforcementFullModel: created enforcement set
        """
        self.check_set_exists(value=name)

        root: FoldersModel = self.folders.get()
        folder: FolderModel = root.resolve_folder(folder=folder, create=create, echo=echo)

        main = self.get_set_action(
            name=main_action_name, action_type=main_action_type, config=main_action_config
        )

        triggers = []
        sq = self.get_trigger_view(query_name=query_name, query_type=query_type)
        if sq:
            triggers.append(
                EnforcementSchedule.get_trigger(
                    query_uuid=sq.uuid,
                    query_type=query_type,
                    schedule_type=schedule_type,
                    schedule_hour=schedule_hour,
                    schedule_minute=schedule_minute,
                    schedule_recurrence=schedule_recurrence,
                    only_new_assets=only_new_assets,
                    on_count_above=on_count_above,
                    on_count_below=on_count_below,
                    on_count_increased=on_count_increased,
                    on_count_decreased=on_count_decreased,
                )
            )

        create_response = self._create(
            name=name, main=main, triggers=triggers, description=description, folder_id=folder.id
        )

        # NEAT: can not move to/from public /private in enforcements
        if folder.depth > 1 and folder.id != create_response.folder.id:
            self._move_sets(folder_id=folder.id, enforcements_ids=create_response.uuid)

        created = self.get_set(value=create_response)
        return created

    def delete(self, value: MULTI_SET) -> EnforcementFullModel:
        """Delete an enforcement set.

        Args:
            value: enforcement set model or str with name or uuid

        Returns:
            EnforcementFullModel: deleted enforcement set
        """
        obj = self.get_set(value=value)
        self._delete(uuid=obj.uuid)
        return obj

    def get_set_action(
        self,
        name: str,
        action_type: MULTI_ACTION_TYPE,
        config: t.Optional[dict] = None,
    ) -> dict:
        """Get the action dictionary needed to add an action to an enforcement set.

        Args:
            name: name to assign to action
            action_type: action type to use
            config: action config

        Returns:
            dict: action dictionary
        """
        action_type = self.get_action_type(value=action_type)
        config = action_type.check_config(config=config)

        msg = """CAUTION:
Enforcement Sets will be forced to the /Drafts folder if:
- Any configuration supplied for any action is invalid
- No Saved Query is supplied for the trigger

Easiest way to learn the correct configuration for an action:
- Create an Enforcement Set using the GUI
- export the Enforcement Set in JSON format using:
  axonshell enforcements get -v "enforcement name" -xf json
- Get the 'config' dictionary for the action you want to use from the JSON output
- Use the 'config' dictionary as appropriate 'config' argument for this method
"""
        warnings.warn(message=msg, category=ApiWarning)

        return EnforcementFullModel.get_action_obj(
            name=name, action_type=action_type, config=config
        )

    def get_trigger_view(
        self,
        query_name: t.Optional[MULTI_SQ] = EnforcementDefaults.query_name,
        query_type: t.Union[QueryTypes, str] = EnforcementDefaults.query_type,
    ) -> t.Optional[SavedQuery]:
        """Get the saved query for use in adding a query to an enforcement.

        Args:
            query_name: Name of Saved Query
            query_type: Type of Saved Query

        Returns:
            SavedQuery: None if query_name is not supplied, otherwise saved query model
        """
        if query_name:
            query_type = QueryTypes.get_value_by_value(query_type)
            return self._triggers_map[query_type].saved_query.get_by_multi(
                sq=query_name, as_dataclass=True
            )
        return None

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from .. import Devices, Instances, Users, Vulnerabilities

        self.api_devices: Devices = Devices(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.api_users: Users = Users(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.api_vulnerabilities: Vulnerabilities = Vulnerabilities(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.api_instances: Instances = Instances(auth=self.auth, **kwargs)
        """API model for cross reference."""

        self.tasks: Tasks = Tasks(auth=self.auth, **kwargs)
        """API model for working with tasks for enforcements."""

    @property
    def _triggers_map(self) -> dict:
        """Map of query types to api objects."""
        return {
            QueryTypes.devices.value: self.api_devices,
            QueryTypes.users.value: self.api_users,
            QueryTypes.vulnerabilities.value: self.api_vulnerabilities,
        }

    def _delete(self, uuid: str) -> json_api.generic.Deleted:
        """Delete an enforcement set by UUID.

        Args:
            uuid: UUID of set to delete

        Returns:
            json_api.generic.Deleted: deleted model
        """
        api_endpoint = ApiEndpoints.enforcements.delete_set
        request_obj = api_endpoint.load_request(value={"ids": [uuid], "include": True})
        response = api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)
        self.get_sets_cached.cache_clear()
        return response

    def _copy(self, uuid: str, name: str, clone_triggers: bool) -> EnforcementFullModel:
        """Copy an enforcement set.

        Args:
            uuid: UUID of set to copy
            name: name to give copy
            clone_triggers: copy triggers into new set

        Returns:
            EnforcementFullModel: copied set
        """
        api_endpoint = ApiEndpoints.enforcements.copy_set
        request_obj = api_endpoint.load_request(
            id=uuid, uuid=uuid, name=name, clone_triggers=clone_triggers
        )
        response = api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)
        self.get_sets_cached.cache_clear()
        return response

    def _update_description(self, uuid: str, description: str) -> None:
        """Update the description of an enforcement set.

        Args:
            uuid: UUID of set to update
            description: description to set

        """
        api_endpoint = ApiEndpoints.enforcements.update_description
        request_obj = api_endpoint.load_request(description=description)
        response = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, uuid=uuid
        )
        self.get_sets_cached.cache_clear()
        return response

    def _update(
        self,
        uuid: str,
        name: str,
        actions: dict,
        folder_id: str = "",
        triggers: t.Optional[t.List[dict]] = None,
    ) -> EnforcementFullModel:
        """Update an enforcement set.

        Args:
            uuid: UUID of set to update
            name: name of set
            actions: actions of set
            triggers: triggers of set

        Returns:
            EnforcementFullModel: updated set
        """
        api_endpoint = ApiEndpoints.enforcements.update_set
        request_obj = api_endpoint.load_request(
            uuid=uuid,
            id=uuid,
            name=name,
            actions=actions,
            triggers=triggers or [],
            folder_id=folder_id,
        )
        response = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, uuid=uuid
        )
        self.get_sets_cached.cache_clear()
        return response

    def _create_from_model(self, request_obj: CreateEnforcementModel) -> EnforcementFullModel:
        """Pass."""
        api_endpoint = ApiEndpoints.enforcements.create_set
        response: EnforcementFullModel = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        self.get_sets_cached.cache_clear()
        return response

    def _create(
        self,
        name: str,
        main: dict,
        folder_id: str = "",
        description: str = "",
        success: t.Optional[t.List[dict]] = None,
        failure: t.Optional[t.List[dict]] = None,
        post: t.Optional[t.List[dict]] = None,
        triggers: t.Optional[t.List[dict]] = None,
    ) -> EnforcementFullModel:
        """Create an enforcement set.

        Args:
            name: name of enforcement to create
            main: main action
            success: success actions
            failure: failure actions
            post: post actions
            triggers: saved query trigger

        Returns:
            EnforcementFullModel: created set
        """
        actions = {
            "main": main,
            "success": success or [],
            "failure": failure or [],
            "post": post or [],
        }
        api_endpoint = ApiEndpoints.enforcements.create_set
        request_obj = api_endpoint.load_request(
            name=name,
            actions=actions,
            triggers=triggers or [],
            description=description,
            folder_id=folder_id,
        )
        response = api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)
        self.get_sets_cached.cache_clear()
        return response

    # noinspection PyShadowingBuiltins
    def _get_sets(
        self,
        limit: int = MAX_PAGE_SIZE,
        offset: int = 0,
        sort: t.Optional[str] = None,
        filter: t.Optional[str] = None,
        search: str = "",
    ) -> t.List[EnforcementBasicModel]:
        """Get enforcement sets in basic model.

        Args:
            limit: limit to N rows per page
            offset: start at row N
            sort: sort based on a model attribute
            filter: AQL filter
            search: search string

        Returns:
            t.List[EnforcementBasicModel]: basic models
        """
        api_endpoint = ApiEndpoints.enforcements.get_sets
        request_obj = api_endpoint.load_request(
            page={"limit": limit, "offset": offset}, filter=filter, search=search, sort=sort
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _get_set(self, uuid: str) -> EnforcementFullModel:
        """Get an enforcement set in full model.

        Args:
            uuid: UUID of set to get

        Returns:
            EnforcementFullModel: full model
        """
        api_endpoint = ApiEndpoints.enforcements.get_set
        return api_endpoint.perform_request(http=self.auth.http, uuid=uuid)

    def _get_action_types(self) -> t.List[ActionType]:
        """Get all action types.

        Returns:
            t.List[ActionType]: action type models
        """
        api_endpoint = ApiEndpoints.enforcements.get_action_types
        return api_endpoint.perform_request(http=self.auth.http)

    def _run_set_against_trigger(
        self, uuid: str, ec_page_run: bool = False, use_conditions: bool = False
    ) -> json_api.generic.Name:
        """Run an enforcement set against its trigger.

        Args:
            uuid: UUID of enforcement set to trigger
            ec_page_run: this was triggered from the EC Page in the GUI
            use_conditions: use conditions configured on enforcement set to determine execution

        """
        api_endpoint = ApiEndpoints.enforcements.run_set_against_trigger
        request_obj = api_endpoint.load_request(
            ec_page_run=ec_page_run, use_conditions=use_conditions
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj, uuid=uuid)

    def _move_sets(
        self, folder_id: str, enforcements_ids: t.Union[str, t.List[str]]
    ) -> MoveEnforcementsResponseModel:
        """Move enforcements to a folder.

        Args:
            folder_id: ID of folder to move enforcements to
            enforcements_ids: list of uuids to move
        """
        api_endpoint = ApiEndpoints.enforcements.move_sets

        request_obj: MoveEnforcementsRequestModel = api_endpoint.load_request(
            folder_id=folder_id, enforcements_ids=listify(enforcements_ids)
        )
        response: MoveEnforcementsResponseModel = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        return response

    def _run_sets_against_trigger(
        self, uuids: t.List[str], include: bool = True, use_conditions: bool = False
    ) -> json_api.generic.ListDictValue:
        """Run enforcement sets against their triggers.

        Args:
            uuids: UUIDs of enforcement sets to trigger
            include: select UUIDs in DB or UUIDs NOT in DB
            use_conditions: use conditions configured on enforcement set to determine execution

        """
        api_endpoint = ApiEndpoints.enforcements.run_sets_against_trigger
        value = {"ids": listify(uuids), "include": include}
        request_obj = api_endpoint.load_request(
            value=value,
            include=include,
            use_conditions=use_conditions,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def run(
        self, values: t.List[str], use_conditions: bool = False, error: bool = True
    ) -> t.List[EnforcementFullModel]:
        """Run enforcement sets against their triggers.

        Args:
            values: names or UUIDs of enforcement sets to trigger
            use_conditions: use conditions
                configured on enforcement set to determine execution
            error: throw error if an enforcement set has no trigger

        """
        cache = self.get_sets()
        items = [self.get_set(value=x, cache=cache) for x in listify(values)]
        to_run = []
        for item in items:
            if item.check_trigger_exists(msg="run enforcement set", error=error):
                to_run.append(item)

        if not to_run:
            raise ApiError(f"No enforcement sets with triggers found from values: {values!r}")

        uuids = [x.uuid for x in to_run]
        if len(uuids) == 1:
            result = self._run_set_against_trigger(uuid=uuids[0], use_conditions=use_conditions)
        else:
            result = self._run_sets_against_trigger(uuids=uuids, use_conditions=use_conditions)

        self.LOG.info(
            f"Ran enforcement sets uuids {uuids} with use_conditions={use_conditions}\n"
            f"Result: {result}"
        )
        return to_run
