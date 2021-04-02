# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from ...tools import dt_parse, int_days_map, json_load
from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import SchemaDatetime, get_field_dc_mm
from .generic import Deleted


class EnforcementBasicSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    last_updated = SchemaDatetime(allow_none=True)
    updated_by = marshmallow_jsonapi.fields.Str(allow_none=True)
    actions_main = marshmallow_jsonapi.fields.Str()
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
        return EnforcementBasic

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs) -> Union[dict, DataModel]:
        """Pass."""
        data = {k.replace(".", "_"): v for k, v in data.items()}
        return data


@dataclasses.dataclass
class EnforcementBasic(DataModel):
    """Pass."""

    id: str
    name: str
    date_fetched: str
    updated_by: str
    actions_main_type: str
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

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementBasicSchema

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
            "uuid",
            "actions_main",
            "actions_main_type",
        ]

    def to_tablize(self):
        """Pass."""
        return {self._human_key(k): getattr(self, k, None) for k in self._str_properties()}

    def get_full(self) -> "Enforcement":
        """Pass."""
        full = self.CLIENT.enforcements._get_by_uuid(uuid=self.uuid)
        full._basic = self
        # PBUG: attrs in details should be in full object as well (updated by)
        # PBUG: should have a call to return all full objects in paging
        return full

    def delete(self) -> Deleted:
        """Pass."""
        return self.CLIENT.enforcements._delete(uuid=self.uuid)


class EnforcementSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return Enforcement


@dataclasses.dataclass
class Enforcement(DataModel):
    """Pass."""

    id: str
    uuid: str
    name: str
    date_fetched: str
    actions: dict
    triggers: List[dict]

    # SAVE_ON_UPDATE: bool = True
    # XXX

    @property
    def schedule_enabled(self) -> bool:
        """Pass."""
        return self._schedule_type and self._schedule_type != "never"

    @property
    def schedule_type(self) -> str:
        """Pass."""
        return self._map_schedule_type["type"]

    @property
    def schedule_recurrence(self) -> str:
        """Pass."""
        type_map = self._map_schedule_type
        tmpl = type_map["recurrence"]
        rmapper = type_map.get("recurrence_mapper")

        time = self.schedule_time
        recurrence = self._schedule_recurrence
        recurrence = rmapper(value=recurrence) if rmapper else recurrence

        return tmpl.format(recurrence=recurrence, time=time)

    @property
    def schedule_time(self) -> str:
        """Pass."""
        return self._trigger_obj.get("period_time", "")

    @property
    def trigger_type(self) -> str:
        """Pass."""
        return self._trigger_view.get("entity", "")

    @property
    def trigger_id(self) -> str:
        """Pass."""
        return self._trigger_view.get("id", "")

    @property
    def trigger_name(self) -> str:
        """Pass."""
        return self.get_basic().triggers_view_name

    @property
    def trigger_run_last(self) -> Optional[datetime.datetime]:
        """Pass."""
        return self.get_basic().triggers_last_triggered

    @property
    def trigger_run_count(self) -> int:
        """Pass."""
        return self.get_basic().triggers_times_triggered

    @property
    def run_on(self) -> str:
        """Pass."""
        return self._trigger_obj.get("run_on", "")

    @property
    def run_on_added_entities_only(self) -> bool:
        """Pass."""
        return self.run_on != "AllEntities"

    @property
    def only_run_when_assets_added(self) -> bool:
        """Pass."""
        return self._conditions.get("new_entities", False)

    @property
    def only_run_when_assets_removed(self) -> bool:
        """Pass."""
        return self._conditions.get("previous_entities", False)

    @property
    def only_run_when_asset_count_above(self) -> Optional[int]:
        """Pass."""
        return self._conditions.get("above", None)

    @property
    def only_run_when_asset_count_below(self) -> Optional[int]:
        """Pass."""
        return self._conditions.get("below", None)

    @property
    def updated_on(self) -> datetime.datetime:
        """Pass."""
        return self.get_basic().last_updated

    @property
    def updated_by(self) -> str:
        """Pass."""
        return self.get_basic().updated_by.get("user_name", "")

    @property
    def updated_by_first_name(self) -> str:
        """Pass."""
        return self.get_basic().updated_by.get("first_name", "")

    @property
    def updated_by_last_name(self) -> str:
        """Pass."""
        return self.get_basic().updated_by.get("last_name", "")

    @property
    def updated_by_full_name(self) -> str:
        """Pass."""
        items = [self.updated_by_first_name, self.updated_by_last_name]
        return " ".join([x for x in items if x])

    def get(self) -> "Enforcement":
        """Pass."""
        return self.CLIENT.enforcements.get_by_uuid(value=self.uuid)

    def save(self) -> "Enforcement":
        """Pass."""

    def copy(self, name: str) -> "Enforcement":
        """Pass."""
        # XXX more details here?

    def delete(self) -> Deleted:
        """Pass."""
        return self.CLIENT.enforcements._delete(uuid=self.uuid)

    # def get_trigger_sq(self) -> dict:
    #     """Pass."""
    #     if self.trigger_id:
    #         apiobj = getattr(self.CLIENT, self.trigger_type)
    #         sq = apiobj.saved_query.get_by_uuid(value=self.trigger_id)
    #         return sq
    #     return {}

    def get_tasks(self):
        """Pass."""
        # XXX

    def get_basic(self, refresh: bool = False) -> "EnforcementBasic":
        """Pass."""
        if not getattr(self, "_basic", None) or refresh:
            self._basic = self.CLIENT.enforcements.get_by_uuid(value=self.uuid, full=False)
        return self._basic

    def set_name(self, value: str):
        """Pass."""
        # XXX

    def set_main_action(type: str, name: str, **kwargs):
        """Pass."""
        # XXX

    def remove_trigger(self):
        """Pass."""
        # XXX

    def set_trigger(self, type: str, name: str, run_on_added_entities_only: bool = False):
        """Pass."""
        # XXX

    def set_run_on_added_entities_only(self, value: bool):
        """Pass."""
        # XXX

    def set_schedule_disabled(self):
        """Pass."""
        """
        period: "never"
        period_recurrence: 99999
        period_time: "13:00"

        dont change period_time if it's there
        add period_time as 13:00 if it's not there
        """
        # XXX

    def set_schedule_every_discovery(self):
        """Pass."""
        """
        period: "all"
        period_time: "13:00" (UTC) (ignored for this one?)

        remove period_recurrence if its there
        dont change period_time if it's there
        add period_time as 13:00 if it's not there
        """
        # XXX

    def set_schedule_hourly(self, hours: int = 12):
        """Pass."""
        """
        period: "hourly"
        period_recurrence: 12 (MIN: 1, MAX: 24)
        period_time: "13:00" (UTC) (ignored for this one?)

        dont change period_time if it's there
        add period_time as 13:00 if it's not there
        """
        # XXX

    def set_schedule_monthly(self, days: List[int], hour: int = 13, minute: int = 00):
        """Pass."""
        """
        period: "monthly"
        period_recurrance: ["1", "8", "7", "5", "3", "28", "29"] (min: 1, max 29?)
        period_time: "13:00" (UTC)

        GUI shows 29 as "last day", it doesn't have 29 or 30 or 31
        """
        # XXX

    def set_schedule_daily(self, days: int = 1, hour: int = 13, minute: int = 00):
        """Pass."""
        """
        period: "daily"
        period_recurrence: 2 (every 2 days) (MIN: 1)
        period_time: "13:00" (UTC)
        """
        # XXX

    def set_schedule_weekly(
        self,
        sunday: bool = True,
        monday: bool = True,
        tuesday: bool = True,
        wednesday: bool = True,
        thursday: bool = True,
        friday: bool = True,
        saturday: bool = True,
        hour: int = 13,
        minute: int = 00,
    ):
        """Pass."""
        """
        period: "weekly"
        period_recurrence: ["0", "1", "2", "3", "4", "6"] (every day cept sat)
        period_time: "13:00" (UTC)
        """
        # XXX

    def set_conditions(
        self,
        on_count_above: Optional[int] = None,
        on_count_below: Optional[int] = None,
        on_count_increased: Optional[bool] = None,
        on_count_decreased: Optional[bool] = None,
    ):
        """Pass."""
        # exception when no trigger
        # XXX

    def add_success_action(self, type: str, name: str, **kwargs):
        """Pass."""

    def add_failure_action(self, type: str, name: str, **kwargs):
        """Pass."""

    def add_post_action(self, type: str, name: str, **kwargs):
        """Pass."""

    def remove_success_action(self, name: str):
        """Pass."""

    def remove_failure_action(self, name: str):
        """Pass."""

    def remove_post_action(self, name: str):
        """Pass."""

    def _add_action(self, condition: str, type: str, name: str, **kwargs):
        """Pass."""

    def _remove_action(self, condition: str, name: str):
        """Pass."""

    def update_action_config(self, name: str, **kwargs):
        """Pass."""

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementSchema

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
        ]
        return "\n".join(items)

    def _get_updated_str(self) -> str:
        """Pass."""
        dt_str = self.updated_on.isoformat() if self.updated_on else "Unknown"
        items = [
            f"Date: {dt_str}",
            f"User Name: {self.updated_by}",
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
                f"Run on added entities only: {self.run_on_added_entities_only}",
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

    @property
    def _conditions(self) -> dict:
        return self._trigger_obj.get("conditions", {})

    @property
    def _schedule_type_maps(self) -> dict:
        return {
            "never": {"type": "None", "recurrence": "n/a"},
            "all": {"type": "Every Discovery Cycle", "recurrence": "n/a"},
            "hourly": {"type": "Every X hours", "recurrence": "every {recurrence} hours"},
            "daily": {
                "type": "Every X days",
                "recurrence": "{time} UTC every {recurrence} days",
            },
            "weekly": {
                "type": "Days of week",
                "recurrence": "{time} UTC on {recurrence}",
                "recurrence_mapper": self._map_weekly_days,
            },
            "monthly": {
                "type": "Days of month",
                "recurrence": "{time} UTC on days {recurrence}",
                "recurrence_mapper": self._map_monthly_days,
            },
            "unknown": {
                "type": "UNKNOWN, API Changed??",
                "recurrence": "UNKNOWN, API Changed??",
            },
        }

    @property
    def _map_schedule_type(self) -> dict:
        """Pass."""
        return self._schedule_type_maps.get(
            self._schedule_type, self._schedule_type_maps["unknown"]
        )

    def _map_monthly_days(self, value: List[str]) -> str:
        """Pass."""
        if "29" in value:
            value.pop(value.index("29"))
            value.append("Last Day")
        return ", ".join(value)

    def _map_weekly_days(self, value: List[str]) -> str:
        """Pass."""
        return ", ".join(int_days_map(value=value))

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

    def _check_has_trigger(self):
        """Pass."""
        # XXX


class EnforcementCreateSchema(DataSchemaJson):
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
        return EnforcementCreate


@dataclasses.dataclass
class EnforcementCreate(DataModel):
    """Pass."""

    name: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementCreateSchema
