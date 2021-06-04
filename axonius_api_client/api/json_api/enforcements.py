# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import copy
import dataclasses
import datetime
from typing import Generator, List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from ...data import BaseEnum
from ...exceptions import ApiError
from ...tools import (coerce_bool, coerce_int, coerce_str_to_csv, dt_parse,
                      int_days_map, json_load)
from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm
from .generic import Deleted, StrValue, StrValueSchema

SET_BASIC = "EnforcementSetBasic"
SETS_BASIC = List[SET_BASIC]
SET_FULL = "EnforcementSet"
SET_BOTH = Union[SET_BASIC, SET_FULL]
SET_GEN = Generator[SET_BOTH, None, None]
SET_UNION = Union[SET_GEN, List[SET_BOTH]]
TASK_BASIC = "EnforcementTaskBasic"
TASKS_BASIC = List[TASK_BASIC]
TASK_FULL = "EnforcementTask"
TASK_BOTH = Union[TASK_BASIC, TASK_FULL]
TASK_GEN = Generator[TASK_BOTH, None, None]
TASK_UNION = Union[TASK_GEN, List[TASK_BOTH]]
ACTION_TYPE = "EnforcementActionType"
ACTION_TYPES = List[ACTION_TYPE]
ACTION = "EnforcementAction"
ACTIONS = List[ACTION]


class ActionConditions(BaseEnum):
    """Pass."""

    main: str = "main"
    success: str = "success"
    failure: str = "failure"
    post: str = "post"


class TriggerRunOn(BaseEnum):
    """Pass."""

    all_entities: str = "AllEntities"
    added_entities: str = "AddedEntities"


class TriggerPeriod(BaseEnum):
    """Pass."""

    never: str = "never"
    discovery: str = "all"
    hourly: str = "hourly"
    monthly: str = "monthly"
    daily: str = "daily"
    weekly: str = "weekly"


class EnforcementSetMixins:
    """Pass."""

    def refetch(self) -> Union[SET_BASIC, SET_FULL]:
        """Pass."""
        if isinstance(self, SET_BASIC):
            return self.get_basic(refetch=True)
        return self.get_full(refetch=True)

    def get_basic(self, refetch: bool = False) -> SET_BASIC:
        """Pass."""
        if not getattr(self, "_basic", None) or refetch:
            self._basic = self.CLIENT.enforcements.find_set(value=self.uuid, full=False)
            if isinstance(self, EnforcementSet):
                self._basic._full = self
        return self._basic

    def get_full(self, refetch: bool = False) -> SET_FULL:
        """Pass."""
        if not getattr(self, "_full", None) or refetch:
            self._full = self.CLIENT.enforcements._get_set_by_uuid(uuid=self.uuid)
            if isinstance(self, EnforcementSetBasic):
                self._full._basic = self
        return self._full

    def delete(self) -> Deleted:
        """Pass."""
        return self.CLIENT.enforcements._delete_set(uuid=self.uuid)

    def get_tasks(self, full: bool = True, generator: bool = False) -> TASK_UNION:
        """Pass."""
        # XXX add filters like within_days/success_count/fail_count
        gen = self.CLIENT.enforcements._get_tasks_gen(uuid=self.uuid, full=full)
        return gen if generator else list(gen)

    # def find_task(self, value: str, full: bool = True) -> TASK_BOTH:
    #     """Get a task for an Enforcement Set by uuid.

    #     Args:
    #         set: name of enforcement set set to get tasks for
    #         value: name or uuid of task to get
    #         full: return the basic or full object

    #     Raises:
    #         :exc:`NotFoundError`: if not found
    #     """
    #     data = self.get_tasks(generator=True, full=False)
    #     found = []
    #     for item in data:
    #         if item.uuid == value or item.name == value:
    #             return item.get_full() if full else item
    #         found.append(item)

    #     err = f"Enforcement Set Task with name or UUID of {value!r} not found"

    #     if found:
    #         msg = tablize(value=[x.to_tablize() for x in found], err=err)
    #     else:
    #         msg = f"{err} - no tasks exist!"

    #     raise NotFoundError(msg)

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
            "uuid",
            "main_action_name",
            "main_action_type",
        ]


class EnforcementTaskMixins:
    """Pass."""

    def get_basic(self, refetch: bool = False) -> TASK_BASIC:
        """Pass."""
        if not getattr(self, "_basic", None) or refetch:
            self._basic = self.CLIENT.enforcements.find_task(value=self.uuid, full=False)
            if isinstance(self, EnforcementTask):
                self._basic._full = self
        return self._basic

    def get_full(self, refetch: bool = False) -> TASK_FULL:
        """Pass."""
        if not getattr(self, "_full", None) or refetch:
            self._full = self.CLIENT.enforcements._get_task_by_uuid(uuid=self.uuid)
            if isinstance(self, EnforcementTaskBasic):
                self._full._basic = self
        return self._full

    def get_set(self, full: bool = True, refetch: bool = False) -> SET_BOTH:
        """Pass."""
        if not getattr(self, "_enforcement", None) or refetch:
            self._enforcement = self.CLIENT.enforcements.find_set(value=self.enforcement, full=full)
        return self._enforcement

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
            "uuid",
            "enforcement",
        ]


class EnforcementSetBasicSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    last_updated = SchemaDatetime(allow_none=True)
    updated_by = marshmallow_jsonapi.fields.Str(allow_none=True)
    actions_main = marshmallow_jsonapi.fields.Str()
    actions_main_name = marshmallow_jsonapi.fields.Str()
    actions_main_type = marshmallow_jsonapi.fields.Str()
    triggers_view_name = marshmallow_jsonapi.fields.Str(allow_none=True)
    triggers_last_triggered = marshmallow_jsonapi.fields.Str(allow_none=True)
    triggers_times_triggered = marshmallow_jsonapi.fields.Int(allow_none=True)
    triggers_period = marshmallow_jsonapi.fields.Str(allow_none=True)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementSetBasic

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs) -> Union[dict, DataModel]:
        """Pass."""

        def fixkey(k):
            return k.replace(".", "_")

        data = {fixkey(k): v for k, v in data.items()}
        return data


class EnforcementSetSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())
    updated_by = marshmallow_jsonapi.fields.Str(allow_none=True, missing=None)
    last_updated = SchemaDatetime(allow_none=True, missing=None)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementSet


class EnforcementSetUpdateSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())
    uuid = marshmallow_jsonapi.fields.Str(allow_none=True, missing=None)
    last_updated = SchemaDatetime(allow_none=True, missing=None)
    updated_by = marshmallow_jsonapi.fields.Str(missing=None, allow_none=True)

    class Meta:
        """Pass."""

        type_ = "enforcements_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementSetUpdate

    @marshmallow.post_dump
    def post_dump_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data.pop("id", None)
        data.pop("last_updated", None)
        data.pop("updated_by", None)
        return data


class EnforcementSetUpdateResponseSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())
    uuid = marshmallow_jsonapi.fields.Str(allow_none=True, missing=None)
    last_updated = SchemaDatetime(allow_none=True, missing=None)
    updated_by = marshmallow_jsonapi.fields.Str(missing=None, allow_none=True)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementSetUpdate


class EnforcementSetCreateSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementSetCreate


class EnforcementSetRunSchema(DataSchemaJson):
    """Pass."""

    ec_page_run = SchemaBool(missing=False)
    use_conditions = SchemaBool(missing=False)

    class Meta:
        """Pass."""

        type_ = "run_enforcements_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementSetRun


@dataclasses.dataclass
class EnforcementSetUpdate(EnforcementSetMixins, DataModel):
    """Pass."""

    name: str
    actions: dict
    triggers: List[dict]
    id: Optional[str] = None
    uuid: Optional[str] = None
    updated_by: Optional[str] = None
    last_updated: Optional[str] = None

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementSetUpdateSchema


@dataclasses.dataclass
class EnforcementSetBasic(EnforcementSetMixins, DataModel):
    """Pass."""

    id: str
    name: str
    date_fetched: str
    updated_by: str
    actions_main_type: str
    actions_main_name: str
    triggers_period: Optional[str] = None
    triggers_view_name: Optional[str] = None
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    actions_main: str = marshmallow_jsonapi.fields.Str()
    triggers_last_triggered: Optional[str] = None
    triggers_times_triggered: Optional[int] = None
    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        self.updated_by = json_load(self.updated_by, error=False)

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.id

    @property
    def main_action_name(self):
        """Pass."""
        return self.actions_main

    @property
    def main_action_type(self):
        """Pass."""
        return self.actions_main_type

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementSetBasicSchema


@dataclasses.dataclass
class EnforcementSet(EnforcementSetMixins, DataModel):
    """Pass."""

    id: str
    uuid: str
    name: str
    actions: dict
    triggers: List[dict]
    date_fetched: Optional[str] = None
    updated_by: Optional[str] = None
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )

    @property
    def schedule_enabled(self) -> bool:
        """Check if set has a trigger and if the schedule is enabled."""
        return bool(self._schedule_type and self._schedule_type != "never")

    @property
    def schedule_type(self) -> str:
        """Get a human friendly string describing the schedule of the trigger."""
        return self._map_schedule_type["type"]

    @property
    def schedule_recurrence(self) -> str:
        """Get a human friendly string describing the recurrence for the schedule of the trigger."""
        type_map = self._map_schedule_type
        tmpl = type_map["recurrence"]
        rmapper = type_map.get("recurrence_mapper")

        time = self.schedule_time
        recurrence = self._schedule_recurrence
        recurrence = rmapper(value=recurrence) if rmapper else recurrence

        return tmpl.format(recurrence=recurrence, time=time)

    @property
    def schedule_time(self) -> str:
        """Get the time string that a schedule of the trigger will run at."""
        return self._trigger_obj.get("period_time", "")

    @property
    def trigger_type(self) -> str:
        """Get the type of trigger if one is configured."""
        return self._trigger_view.get("entity", "")

    @property
    def trigger_id(self) -> str:
        """Get the UUID of the saved query for the trigger if one is configured."""
        return self._trigger_view.get("id", "")

    @property
    def trigger_name(self) -> str:
        """Get the name of the saved query for the trigger if one is configured."""
        return self.get_basic().triggers_view_name

    @property
    def trigger_run_last(self) -> Optional[datetime.datetime]:
        """Get the last time a trigger ran if one is configured."""
        return self.get_basic().triggers_last_triggered or None

    @property
    def trigger_run_count(self) -> int:
        """Get the number of times a trigger ran if one is configured."""
        return self.get_basic().triggers_times_triggered or 0

    @property
    def only_run_against_new_assets(self) -> bool:
        """Run enforcement only against assets that have been added since last scheduled run."""
        return bool(self._run_on and self._run_on != str(TriggerRunOn.all_entities))

    @property
    def only_run_when_assets_added(self) -> bool:
        """Run enforcement only when assets have been added since last scheduled run."""
        return self._conditions.get("new_entities", False)

    @property
    def only_run_when_assets_removed(self) -> bool:
        """Run enforcement only when assets have been removed since last scheduled run."""
        return self._conditions.get("previous_entities", False)

    @property
    def only_run_when_asset_count_above(self) -> Optional[int]:
        """Run enforcement only when asset count is above this number."""
        return self._conditions.get("above", None)

    @property
    def only_run_when_asset_count_below(self) -> Optional[int]:
        """Run enforcement only when asset count is below this number."""
        return self._conditions.get("below", None)

    @property
    def updated_on(self) -> datetime.datetime:
        """Get the last date time this set was updated."""
        return self.get_basic().last_updated

    @property
    def updated_by_user_name(self) -> str:
        """Get the user name of the user that last updated this set."""
        return self.get_basic().updated_by.get("user_name", "")

    @property
    def updated_by_first_name(self) -> str:
        """Get the first name of the user that last updated this set."""
        return self.get_basic().updated_by.get("first_name", "")

    @property
    def updated_by_last_name(self) -> str:
        """Get the last name of the user that last updated this set."""
        return self.get_basic().updated_by.get("last_name", "")

    @property
    def updated_by_full_name(self) -> str:
        """Get the first and last name of the user that last updated this set."""
        items = [self.updated_by_first_name, self.updated_by_last_name]
        return " ".join([x for x in items if x])

    @property
    def has_running_task(self) -> bool:
        """Check if this set currently has a running task."""
        return self.CLIENT.enforcements._set_has_running_task(name=self.name).value

    @property
    def main_action_name(self):
        """Get the name of the main action configured for this set."""
        return self.actions["main"]["name"]

    @property
    def main_action_type(self):
        """Get the type of the main action configured for this set."""
        return self.actions["main"]["action"]["action_name"]

    def save(self) -> SET_FULL:
        """Save any changes made to this set."""
        # XXX check for name collisions in actions! use self.action_names
        # we toss the update response away because it doesn't return full objects for actions
        self.CLIENT.enforcements._update_set(
            uuid=self.uuid, name=self.name, actions=self.actions, triggers=self.triggers
        )
        return self.get_full(refetch=True)

    def run(self, use_conditions: bool = False, ec_page_run: bool = False) -> SET_FULL:
        """Run this set."""
        self._trigger_obj_copy(msg="run")
        self.CLIENT.enforcements._run_set(
            uuid=self.uuid, use_conditions=use_conditions, ec_page_run=ec_page_run
        )
        return self.get_full(refetch=True)

    def set_main_action(self, name: str, type: str, **kwargs):
        """Set the main action for this set."""
        action_type = self.CLIENT.enforcements.find_action_type(value=type)
        action_config = kwargs  # XXX
        actions = {
            "main": {
                "name": name,
                "action": {"action_name": action_type.name, "config": action_config},
            },
            "success": self.actions.get("success", []),
            "failure": self.actions.get("failure", []),
            "post": self.actions.get("post", []),
        }

        new_obj = self.replace_attrs(actions=actions)
        return new_obj

    def remove_trigger(self) -> SET_FULL:
        """Remove the trigger and trigger schedule for this set."""
        self._trigger_obj_copy(msg="remove trigger")
        new_obj = self.replace_attrs(triggers=[])
        return new_obj

    def set_trigger(self, name: str, type: str) -> SET_FULL:
        """Configure the trigger for this set."""
        trigger = self._trigger_obj_copy() if self._trigger_obj else self._trigger_obj_new()
        trigger["view"] = self._find_trigger(name=name, type=type)
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def set_conditions(
        self,
        on_count_above: Optional[int] = None,
        on_count_below: Optional[int] = None,
        on_count_increased: Optional[bool] = None,
        on_count_decreased: Optional[bool] = None,
    ):
        """Pass."""
        trigger = self._trigger_obj_copy(msg="set trigger conditions")
        trigger["conditions"] = self._create_conditions(
            on_count_above=on_count_above,
            on_count_below=on_count_below,
            on_count_increased=on_count_increased,
            on_count_decreased=on_count_decreased,
        )
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def set_only_run_against_new_assets(self, value: bool):
        """Configure the trigger for this set to only run against new assets or all assets."""
        trigger = self._trigger_obj_copy(msg="set 'only_run_against_new_assets'")
        trigger["run_on"] = self._get_run_on(value=value)
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def set_schedule_disabled(self):
        """Pass."""
        """
        period: "never"
        period_recurrence: 99999
        period_time: "13:00"

        dont change period_time if it's there
        add period_time as 13:00 if it's not there
        """
        trigger = self._trigger_obj_copy(msg="disable trigger schedule")
        trigger["period"] = TriggerPeriod.never.value
        trigger["period_time"] = trigger.get("period_time", self._build_period_time())
        trigger.pop("period_recurrence", None)
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def set_schedule_every_discovery(self):
        """Pass."""
        """
        period: "all"
        period_time: "13:00" (UTC) (ignored for this one?)

        remove period_recurrence if its there
        dont change period_time if it's there
        add period_time as 13:00 if it's not there
        """
        trigger = self._trigger_obj_copy(msg="set trigger schedule to every discovery")
        trigger["period"] = TriggerPeriod.discovery.value
        trigger["period_time"] = trigger.get("period_time", self._build_period_time())
        trigger.pop("period_recurrence", None)
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def set_schedule_hourly(self, hours: int = 12):
        """Pass."""
        """
        period: "hourly"
        period_recurrence: 12 (MIN: 1, MAX: 24)
        period_time: "13:00" (UTC) (ignored for this one?)

        dont change period_time if it's there
        add period_time as 13:00 if it's not there
        """
        trigger = self._trigger_obj_copy(msg="set trigger schedule to hourly")
        trigger["period"] = TriggerPeriod.hourly.value
        trigger["period_time"] = trigger.get("period_time", self._build_period_time())
        trigger["period_recurrence"] = coerce_int(obj=hours, max_value=24, min_value=1)
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def set_schedule_monthly(self, days: List[int], hour: int = 13, minute: int = 0):
        """Pass."""
        """
        period: "monthly"
        period_recurrance: ["1", "8", "7", "5", "3", "28", "29"] (min: 1, max 29?)
        period_time: "13:00" (UTC)

        GUI shows 29 as "last day", it doesn't have 29 or 30 or 31
        """
        trigger = self._trigger_obj_copy(msg="set trigger schedule to monthly")
        trigger["period"] = TriggerPeriod.monthly.value
        trigger["period_time"] = self._build_period_time(hour=hour, minute=minute)
        trigger["period_recurrence"] = [
            str(coerce_int(obj=x, min_value=1, max_value=29))
            for x in coerce_str_to_csv(value=days, coerce_list=True)
        ]
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def set_schedule_daily(self, days: int = 1, hour: int = 13, minute: int = 00):
        """Pass."""
        """
        period: "daily"
        period_recurrence: 2 (every 2 days) (MIN: 1)
        period_time: "13:00" (UTC)
        """
        trigger = self._trigger_obj_copy(msg="set trigger schedule to daily")
        trigger["period"] = TriggerPeriod.daily.value
        trigger["period_time"] = self._build_period_time(hour=hour, minute=minute)
        trigger["period_recurrence"] = coerce_int(obj=days, min_value=1)
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def set_schedule_weekly(
        self, days: Union[str, List[Union[str, int]]], hour: int = 13, minute: int = 00
    ):
        """Pass."""
        """
        period: "weekly"
        period_recurrence: ["0", "1", "2", "3", "4", "6"] (every day cept sat)
        period_time: "13:00" (UTC)
        """
        trigger = self._trigger_obj_copy(msg="set trigger schedule to weekly")
        trigger["period"] = TriggerPeriod.weekly.value
        trigger["period_time"] = self._build_period_time(hour=hour, minute=minute)
        trigger["period_recurrence"] = int_days_map(value=days, names=False)
        new_obj = self.replace_attrs(triggers=[trigger])
        return new_obj

    def add_action(self, phase: str, type: str, name: str, **kwargs):
        """Pass."""
        # XXX success, failure, post

    def remove_action(self, phase: str, name: str):
        """Pass."""

    def update_action_config(self, phase: str, name: str, **kwargs):
        """Pass."""

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementSetSchema

    def __str__(self) -> List[str]:
        """Pass."""
        items = [
            self._get_name_str(),
            self._get_updated_str(),
            self._get_actions_str("main"),
            self._get_actions_str("success"),
            self._get_actions_str("failure"),
            self._get_actions_str("post"),
            self._get_trigger_str(),
            self._get_schedule_str(),
        ]
        return "\n".join(items)

    def _get_name_str(self) -> str:
        """Pass."""
        items = [
            f"Name: {self.name}",
            f"UUID: {self.uuid}",
            f"Has running task: {self.has_running_task}",
        ]
        return "\n".join(items)

    def _get_updated_str(self) -> str:
        """Pass."""
        dt_str = self.updated_on.isoformat() if self.updated_on else "Unknown"
        items = [
            f"Date: {dt_str}",
            f"User Name: {self.updated_by_user_name}",
            f"Full Name: {self.updated_by_full_name}",
        ]
        return "Updated:\n  " + "\n  ".join(items)

    def _get_trigger_str(self) -> str:
        """Pass."""
        if self.trigger_name:

            if self.trigger_run_last:
                last_ran = dt_parse(obj=self.trigger_run_last, default_tz_utc=True).isoformat()
            else:
                last_ran = "never"

            items = [
                f"Type: {self.trigger_type.title()}",
                f"Name: {self.trigger_name}",
                f"UUID: {self.trigger_id}",
                f"Run on added entities only: {self.only_run_against_new_assets}",
                f"Last ran on: {last_ran}",
                f"Run count: {self.trigger_run_count}",
            ]
        else:
            items = ["None"]
        return "Trigger:\n  " + "\n  ".join(items)

    def _get_schedule_str(self) -> str:
        """Pass."""
        if self.schedule_enabled:
            oad = self.only_run_when_assets_added
            oar = self.only_run_when_assets_removed
            oca = self.only_run_when_asset_count_above or False
            ocb = self.only_run_when_asset_count_below or False

            items = [
                f"Type: {self.schedule_type}",
                f"Recurrence: {self.schedule_recurrence}",
                f"Only run when assets have been added since the last execution: {oad}",
                f"Only run when assets have been removed since the last execution: {oar}",
                f"Only run when the number of assets is above N: {oca}",
                f"Only run when the number of assets is below N: {ocb}",
            ]
        else:
            items = ["None"]

        return "Schedule:\n  " + "\n  ".join(items)

    def _get_actions_str(self, category: str) -> str:
        """Pass."""

        def deets(obj):
            aname = obj["name"]
            atype = obj["action"]["action_name"]
            return f"Name: {aname!r}, Type: {atype!r} "

        cat = category.title()
        actions = self.actions[category]
        if isinstance(actions, dict):
            return f"{cat} Action:\n  {deets(actions)}"

        if not actions:
            return f"{cat} Actions:\n  None"

        items = [deets(x) for x in actions]
        return f"{cat} Actions:\n  " + "\n  ".join(items)

    @property
    def _conditions(self) -> dict:
        return self._trigger_obj.get("conditions", {})

    @property
    def _schedule_type_maps(self) -> dict:
        return {
            TriggerPeriod.never.value: {"type": "None", "recurrence": "n/a"},
            TriggerPeriod.discovery.value: {"type": "Every Discovery Cycle", "recurrence": "n/a"},
            TriggerPeriod.hourly.value: {
                "type": "Every X hours",
                "recurrence": "every {recurrence} hours",
            },
            TriggerPeriod.daily.value: {
                "type": "Every X days",
                "recurrence": "{time} UTC every {recurrence} days",
            },
            TriggerPeriod.weekly.value: {
                "type": "Days of week",
                "recurrence": "{time} UTC on {recurrence}",
                "recurrence_mapper": self._map_weekly_days,
            },
            TriggerPeriod.monthly.value: {
                "type": "Days of month",
                "recurrence": "{time} UTC on days {recurrence}",
                "recurrence_mapper": self._map_monthly_days,
            },
            "unknown": {
                "type": "UNKNOWN, API Changed??",
                "recurrence": "UNKNOWN, API Changed??",
            },
        }

    def _trigger_obj_copy(self, msg: str = ""):
        """Pass."""
        if not self._trigger_obj and msg:
            info = f"named {self.name!r} (UUID {self.uuid!r})"
            msg = f"Unable to {msg} - Enforcement Set {info} has no trigger configured"
            raise ApiError(msg)
        return copy.deepcopy(self._trigger_obj)

    @property
    def _triggers_map(self) -> dict:
        """Pass."""
        return {"devices": self.CLIENT.devices, "users": self.CLIENT.users}

    def _find_trigger(self, name: str, type: str) -> dict:
        """Pass."""
        if type not in self._triggers_map:
            valid = ", ".join(list(self._triggers_map))
            raise ApiError(f"Trigger type of {type!r} is not a valid type, valid types: {valid}")

        apiobj = self._triggers_map[type]
        sq = apiobj.saved_query.get_by_name(value=name)
        return {"id": sq["id"], "entity": type}

    @property
    def _map_schedule_type(self) -> dict:
        """Pass."""
        stype = self._schedule_type

        if not stype:
            return self._schedule_type_maps["never"]

        if stype not in self._schedule_type_maps:
            return self._schedule_type_maps["unknown"]

        return self._schedule_type_maps[stype]

    @property
    def _run_on(self) -> str:
        """Pass."""
        return self._trigger_obj.get("run_on", "")

    def _map_monthly_days(self, value: List[str]) -> str:
        """Pass."""
        if "29" in value:
            value.pop(value.index("29"))
            value.append("Last Day")
        return ", ".join(value)

    def _map_weekly_days(self, value: List[str]) -> str:
        """Pass."""
        return ", ".join(int_days_map(value=value, names=True))

    @property
    def _schedule_type(self) -> str:
        """Pass."""
        return self._trigger_obj.get("period", "")

    @property
    def _schedule_recurrence(self) -> Optional[Union[int, str, List[str]]]:
        """Pass."""
        return self._trigger_obj.get("period_recurrence")

    @property
    def _trigger_obj(self) -> dict:
        """Pass."""
        return self.triggers[0] if self.triggers else {}

    @property
    def _trigger_view(self) -> dict:
        """Pass."""
        return self._trigger_obj.get("view", {})

    def _trigger_obj_new(
        self,
        period: str = "never",
        period_time_hour: int = 13,
        period_time_minute: int = 0,
        period_recurrence: Optional[Union[int, List[str]]] = None,
        only_run_against_new_assets: bool = False,
        on_count_above: Optional[int] = None,
        on_count_below: Optional[int] = None,
        on_count_increased: bool = False,
        on_count_decreased: bool = False,
        **kwargs,
    ) -> dict:
        """Pass."""
        ret = {}
        ret["name"] = "Trigger"
        ret["view"] = None
        ret["period"] = period
        ret["period_time"] = self._build_period_time(
            hour=period_time_hour, minute=period_time_minute
        )

        if period_recurrence:
            ret["period_recurrence"] = period_recurrence

        ret["conditions"] = self._create_conditions(
            on_count_above=on_count_above,
            on_count_below=on_count_below,
            on_count_increased=on_count_increased,
            on_count_decreased=on_count_decreased,
        )

        ret["run_on"] = self._get_run_on(value=only_run_against_new_assets)
        return ret

    @staticmethod
    def _create_conditions(
        on_count_above: Optional[int] = None,
        on_count_below: Optional[int] = None,
        on_count_increased: bool = False,
        on_count_decreased: bool = False,
    ) -> dict:
        """Pass."""
        return {
            "new_entities": coerce_bool(obj=on_count_increased),
            "previous_entities": coerce_bool(obj=on_count_decreased),
            "above": coerce_int(obj=on_count_above, allow_none=True, minimum=0),
            "below": coerce_int(obj=on_count_below, allow_none=True, minimum=0),
        }

    @staticmethod
    def _get_run_on(value: bool = False) -> str:
        """Pass."""
        return (TriggerRunOn.added_entities if value else TriggerRunOn.all_entities).value

    def _build_period_time(self, hour: int = 13, minute: int = 0) -> str:
        """Pass."""
        hour = coerce_int(obj=hour, min_value=0, max_value=23)
        minute = coerce_int(obj=minute, min_value=0, max_value=59)
        return f"{hour:0>2}:{minute:0>2}"


@dataclasses.dataclass
class EnforcementSetCreate(DataModel):
    """Pass."""

    name: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementSetCreateSchema


@dataclasses.dataclass
class EnforcementSetRun(DataModel):
    """Pass."""

    ec_page_run: bool = False
    use_conditions: bool = False

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementSetRunSchema


class EnforcementTaskBasicSchema(DataSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    finished_at = SchemaDatetime()
    started_at = SchemaDatetime()
    task_name = marshmallow_jsonapi.fields.Str()
    enforcement = marshmallow_jsonapi.fields.Str()
    main_action = marshmallow_jsonapi.fields.Str()
    status = marshmallow_jsonapi.fields.Str()
    successful_total = marshmallow_jsonapi.fields.Str()
    trigger_condition = marshmallow_jsonapi.fields.Str()
    trigger_view = marshmallow_jsonapi.fields.Str()

    class Meta:
        """Pass."""

        type_ = "tasks_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementTaskBasic

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs) -> Union[dict, DataModel]:
        """Pass."""
        data["task_name"] = data.pop("result.metadata.task_name")
        data["enforcement"] = data.pop("result.main.name")
        data["main_action"] = data.pop("result.main.action.action_name")
        data["status"] = data.pop("result.metadata.status")
        data["successful_total"] = data.pop("result.metadata.successful_total")
        data["trigger_condition"] = data.pop("result.metadata.trigger.condition")
        data["trigger_view"] = data.pop("result.metadata.trigger.view.name")
        return data


@dataclasses.dataclass
class EnforcementTaskBasic(EnforcementTaskMixins, DataModel):
    """Pass."""

    id: str
    uuid: str
    date_fetched: str
    task_name: str
    enforcement: str
    main_action: str
    status: str
    successful_total: str
    trigger_condition: str
    trigger_view: str
    started_at: datetime.datetime = get_field_dc_mm(mm_field=SchemaDatetime())
    finished_at: datetime.datetime = get_field_dc_mm(mm_field=SchemaDatetime())
    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    # XXX add things like succes_count, total_count, failure_count

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementTaskBasicSchema


class EnforcementTaskSchema(DataSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str()
    condition = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    enforcement = marshmallow_jsonapi.fields.Str()
    finished = SchemaDatetime()
    result = marshmallow_jsonapi.fields.Dict()
    started = SchemaDatetime()
    task_name = marshmallow_jsonapi.fields.Str()
    trigger_period = marshmallow_jsonapi.fields.Str()
    trigger_view = marshmallow_jsonapi.fields.Str()

    # XXX figure out result
    class Meta:
        """Pass."""

        type_ = "tasks_details_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementTask

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs) -> Union[dict, DataModel]:
        """Pass."""
        data["trigger_period"] = data.pop("period")
        data["trigger_view"] = data.pop("view")
        return data


@dataclasses.dataclass
class EnforcementTask(EnforcementTaskMixins, DataModel):
    """Pass."""

    id: str
    uuid: str
    date_fetched: str
    enforcement: str
    started: datetime.datetime = get_field_dc_mm(mm_field=SchemaDatetime())
    finished: datetime.datetime = get_field_dc_mm(mm_field=SchemaDatetime())
    result: dict
    task_name: str
    trigger_period: str
    trigger_view: str
    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementTaskSchema


class EnforcementActionTypeSchema(DataSchemaJson):
    """Pass."""

    default = marshmallow_jsonapi.fields.Dict()
    schema = marshmallow_jsonapi.fields.Dict()

    class Meta:
        """Pass."""

        type_ = "actions_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementActionType


class EnforcementActionSchema(StrValueSchema):
    """Pass."""

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementAction


@dataclasses.dataclass
class EnforcementActionType(DataModel):
    """Pass."""

    id: str
    default: dict
    schema: dict

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementActionTypeSchema

    @property
    def name(self):
        """Pass."""
        return self.id

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
        ]

    def get_config_parser(self, **kwargs):
        """Pass."""
        from .config_parser import ConfigParser

        kwargs["schema"] = self.schema
        kwargs["defaults"] = self.default
        kwargs["client"] = self.CLIENT
        kwargs["source"] = f"Enforcement Action Type {self.name!r}"
        kwargs["file_upload_cb"] = None  # XXX do me
        kwargs["sane_defaults_key"] = self.name
        return ConfigParser(**kwargs)


class EnforcementAction(StrValue):
    """Pass."""

    id: str

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementActionSchema

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
        ]

    @property
    def name(self) -> str:
        """Pass."""
        return self.value
