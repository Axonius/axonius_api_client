# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import Any, ClassVar, List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from ...data import BaseEnum
from ...exceptions import (
    ApiError,
    ConfigRequired,
    ConfigUnknown,
    NotFoundError,
    NoTriggerDefinedError,
    ToolsError,
)
from ...tools import coerce_bool, coerce_int, coerce_str_to_csv, int_days_map, json_dump, json_load
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaDatetime, get_field_dc_mm


class SetDefaults:
    """Pass."""

    query_name: Optional[str] = None
    query_type: Union["QueryType", str] = "devices"
    schedule_type: Union["Schedule", str] = "never"
    schedule_hour: int = 13
    schedule_minute: int = 0
    schedule_recurrence: Optional[Union[int, List[str]]] = None
    only_new_assets: bool = False
    on_count_above: Optional[int] = None
    on_count_below: Optional[int] = None
    on_count_increased: bool = False
    on_count_decreased: bool = False


class ActionCategory(BaseEnum):
    """Pass."""

    success: str = "success"
    failure: str = "failure"
    post: str = "post"


class QueryType(BaseEnum):
    """Pass."""

    devices: str = "devices"
    users: str = "users"


class OnlyNewAssets(BaseEnum):
    """Pass."""

    all_entities: str = "AllEntities"
    added_entities: str = "AddedEntities"

    @classmethod
    def get_str(cls, value: bool = False) -> str:
        """Pass."""
        value = coerce_bool(obj=value, errmsg="only_new_assets must be a boolean")
        return str(cls.added_entities if value else cls.all_entities)

    @classmethod
    def get_bool(
        cls, value: Optional[Union["OnlyNewAssets", str]] = all_entities
    ) -> Optional[bool]:
        """Pass."""
        if value is not None:
            value = cls.get_value(value=value)

            if value == cls.added_entities:
                return True

            if value == cls.all_entities:
                return False

        return None


class Schedule(BaseEnum):
    """Pass."""

    never: str = "never"
    discovery: str = "all"
    hourly: str = "hourly"
    monthly: str = "monthly"
    daily: str = "daily"
    weekly: str = "weekly"

    @classmethod
    def get_value(cls, value: Union["Schedule", str] = SetDefaults.schedule_type) -> "Schedule":
        """Pass."""
        return super().get_value(value=value)

    def get_recurrence(self, value: Any = SetDefaults.schedule_recurrence) -> Any:
        """Pass."""
        return getattr(self, f"calc_{self.name}")(value=value)

    @staticmethod
    def get_time(
        hour: int = SetDefaults.schedule_hour, minute: int = SetDefaults.schedule_minute
    ) -> str:
        """Pass."""
        hour = coerce_int(
            obj=hour,
            min_value=0,
            max_value=23,
            errmsg="Schedule time hour value must be an integer between 0 and 23",
        )
        minute = coerce_int(
            obj=minute,
            min_value=0,
            max_value=59,
            errmsg="Schedule time minute value must be an integer between 0 and 59",
        )
        return f"{hour:0>2}:{minute:0>2}"

    @staticmethod
    def get_conditions(
        on_count_above: Optional[int] = SetDefaults.on_count_above,
        on_count_below: Optional[int] = SetDefaults.on_count_below,
        on_count_increased: bool = SetDefaults.on_count_increased,
        on_count_decreased: bool = SetDefaults.on_count_decreased,
    ) -> dict:
        """Pass."""
        return {
            "new_entities": coerce_bool(
                obj=on_count_increased, errmsg="on_count_above must be a boolean"
            ),
            "previous_entities": coerce_bool(
                obj=on_count_decreased, errmsg="on_count_below must be a boolean"
            ),
            "above": coerce_int(
                obj=on_count_above,
                allow_none=True,
                min_value=0,
                errmsg="on_count_increased must be None or an integer above 0",
            ),
            "below": coerce_int(
                obj=on_count_below,
                allow_none=True,
                min_value=0,
                errmsg="on_count_decreased must be None or an integer above 0",
            ),
        }

    @staticmethod
    def get_view(
        query_uuid: Optional[str] = None, query_type: Union[QueryType, str] = SetDefaults.query_type
    ) -> Optional[dict]:
        """Pass."""
        query_type = QueryType.get_value(query_type)
        if isinstance(query_uuid, str) and query_uuid:
            return {"id": query_uuid, "entity": query_type.value}
        return None

    @classmethod
    def get_trigger(
        cls,
        query_uuid: Optional[str] = None,
        query_type: Union[QueryType, str] = SetDefaults.query_type,
        schedule_type: Union["Schedule", str] = SetDefaults.schedule_type,
        schedule_hour: int = SetDefaults.schedule_hour,
        schedule_minute: int = SetDefaults.schedule_minute,
        schedule_recurrence: Optional[Union[int, List[str]]] = SetDefaults.schedule_recurrence,
        only_new_assets: bool = SetDefaults.only_new_assets,
        on_count_above: Optional[int] = SetDefaults.on_count_above,
        on_count_below: Optional[int] = SetDefaults.on_count_below,
        on_count_increased: bool = SetDefaults.on_count_increased,
        on_count_decreased: bool = SetDefaults.on_count_decreased,
    ) -> dict:
        """Pass."""
        schedule_type = cls.get_value(value=schedule_type)
        schedule_recurrence = schedule_type.get_recurrence(value=schedule_recurrence)
        schedule_time = cls.get_time(hour=schedule_hour, minute=schedule_minute)
        conditions = cls.get_conditions(
            on_count_above=on_count_above,
            on_count_below=on_count_below,
            on_count_increased=on_count_increased,
            on_count_decreased=on_count_decreased,
        )
        run_on = OnlyNewAssets.get_str(value=only_new_assets)
        view = cls.get_view(query_uuid=query_uuid, query_type=query_type)

        ret = {}
        ret["name"] = "Trigger"
        ret["view"] = view
        ret["period"] = schedule_type.value
        ret["period_time"] = schedule_time

        if schedule_recurrence is not None:
            ret["period_recurrence"] = schedule_recurrence

        ret["conditions"] = conditions
        ret["run_on"] = run_on
        return ret

    @staticmethod
    def calc_hourly(value: Any = None) -> int:
        """Pass."""
        pre = "Schedule Recurrence of 'hourly'"
        err_value = f"{pre} must be an integer between 1 and 24"
        return coerce_int(obj=value, max_value=24, min_value=1, errmsg=err_value)

    @staticmethod
    def calc_monthly(value: Any = None) -> List[str]:
        """Pass."""
        pre = "Schedule Recurrence of 'monthly'"
        err_values = f"{pre} must be a list or CSV of integers between 1 and 29"
        err_value = f"{pre} must be an integer between 1 and 29"

        values = coerce_str_to_csv(value=value, coerce_list=True, errmsg=err_values)
        value = [coerce_int(obj=x, min_value=1, max_value=29, errmsg=err_value) for x in values]
        return [str(x) for x in sorted(list(set(value)))]

    @staticmethod
    def calc_weekly(value: Any = None) -> List[str]:
        """Pass."""
        pre = "Schedule Recurrence of 'weekly'"
        err_value = f"{pre} must be a list or CSV of integers between 0 and 6 or day names"
        try:
            return int_days_map(value=value, names=False)
        except Exception as exc:
            raise ToolsError(f"{err_value}: {exc}")

    @staticmethod
    def calc_daily(value: Any = None) -> int:
        """Pass."""
        pre = "Schedule Recurrence of 'daily'"
        err_value = f"{pre} must be an integer higher than 1"
        return coerce_int(obj=value, min_value=1, errmsg=err_value)

    @staticmethod
    def calc_never(value: Any = None) -> None:
        """Pass."""
        return None

    @staticmethod
    def calc_discovery(value: Any = None) -> None:
        """Pass."""
        return None


class SetBasicSchema(BaseSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str()
    name = marshmallow_jsonapi.fields.Str()

    actions_main = marshmallow_jsonapi.fields.Str()
    actions_main_name = marshmallow_jsonapi.fields.Str()
    actions_main_type = marshmallow_jsonapi.fields.Str()

    triggers_view_name = marshmallow_jsonapi.fields.Str(allow_none=True)
    triggers_last_triggered = marshmallow_jsonapi.fields.Str(allow_none=True)
    triggers_times_triggered = marshmallow_jsonapi.fields.Int(allow_none=True)
    triggers_period = marshmallow_jsonapi.fields.Str(allow_none=True)

    updated_by = marshmallow_jsonapi.fields.Str(allow_none=True)
    last_triggered = SchemaDatetime(allow_none=True)
    last_updated = SchemaDatetime(allow_none=True)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SetBasic

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs):
        """Pass."""
        return {k.replace(".", "_"): v for k, v in data.items()}


@dataclasses.dataclass
class SetBasic(BaseModel):
    """Pass."""

    id: str
    uuid: str
    name: str

    actions_main: str
    actions_main_name: str
    actions_main_type: str

    triggers_period: Optional[str] = None
    triggers_view_name: Optional[str] = None
    triggers_last_triggered: Optional[str] = None
    triggers_times_triggered: Optional[int] = None

    updated_by: Optional[str] = None
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True, load_default=None, dump_default=None), default=None
    )
    last_triggered: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True, load_default=None, dump_default=None), default=None
    )

    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    @property
    def query_name(self) -> Optional[str]:
        """Pass."""
        return self.triggers_view_name or None

    @property
    def triggered_last_date(self) -> Optional[datetime.datetime]:
        """Pass."""
        return self.last_triggered

    @property
    def triggered_count(self) -> Optional[int]:
        """Pass."""
        return self.triggers_times_triggered

    @property
    def schedule(self) -> Optional[str]:
        """Pass."""
        return self.triggers_period or None

    @property
    def main_action_str(self) -> str:
        """Pass."""
        return f"Main Action: {self.actions_main_name!r} ({self.actions_main_type})"

    @property
    def updated_date(self) -> datetime.datetime:
        """Pass."""
        return self.last_updated

    @property
    def updated_user_obj(self) -> dict:
        """Pass."""
        if not hasattr(self, "_updated_user_obj"):
            self._updated_user_obj = json_load(self.updated_by)
        return self._updated_user_obj

    @property
    def updated_user_name(self) -> str:
        """Get the user name of the user that last updated this set."""
        return self.updated_user_obj.get("user_name", "")

    @property
    def updated_user_source(self) -> str:
        """Get the source of the user that last updated this set."""
        return self.updated_user_obj.get("source", "")

    @property
    def updated_user_first_name(self) -> str:
        """Get the first name of the user that last updated this set."""
        return self.updated_user_obj.get("first_name", "")

    @property
    def updated_user_last_name(self) -> str:
        """Get the last name of the user that last updated this set."""
        return self.updated_user_obj.get("last_name", "")

    @property
    def updated_user_full_name(self) -> str:
        """Get the first and last name of the user that last updated this set."""
        return " ".join(
            [x for x in [self.updated_user_first_name, self.updated_user_last_name] if x]
        )

    @property
    def updated_user(self) -> str:
        """Pass."""
        return f"{self.updated_user_source}/{self.updated_user_name}"

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SetBasicSchema

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            self.main_action_str,
            f"Query Name: {self.query_name}",
            f"Schedule: {self.schedule}",
            f"Triggered Last Date: {self.triggered_last_date}",
            f"Triggered Count: {self.triggered_count}",
            f"Updated Date: {self.updated_date}",
            f"Updated User: {self.updated_user}",
        ]
        return "\n".join(items)

    def to_tablize(self):
        """Pass."""
        ident = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            f"Updated Date: {self.updated_date}",
            f"Updated User: {self.updated_user!r}",
        ]
        details = [
            self.main_action_str,
            f"Query Name: {self.query_name!r}",
            f"Schedule: {self.schedule}",
            f"Triggered Last Date: {self.triggered_last_date}",
            f"Triggered Count: {self.triggered_count}",
        ]
        return {
            "Identifier": "\n".join(ident),
            "Details": "\n".join(details),
        }

    def __repr__(self):
        """Pass."""
        return self.__str__()


class SetFullSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SetFull


@dataclasses.dataclass
class SetFull(BaseModel):
    """Pass."""

    id: str
    uuid: str
    name: str
    actions: dict
    triggers: List[dict]

    BASIC: ClassVar[SetBasic] = None

    def set_trigger(
        self,
        query_uuid: Optional[str] = None,
        query_type: str = SetDefaults.query_type,
        schedule_type: Union["Schedule", str] = SetDefaults.schedule_type,
        schedule_hour: int = SetDefaults.schedule_hour,
        schedule_minute: int = SetDefaults.schedule_minute,
        schedule_recurrence: Optional[Union[int, List[str]]] = SetDefaults.schedule_recurrence,
        only_new_assets: bool = SetDefaults.only_new_assets,
        on_count_above: Optional[int] = SetDefaults.on_count_above,
        on_count_below: Optional[int] = SetDefaults.on_count_below,
        on_count_increased: bool = SetDefaults.on_count_increased,
        on_count_decreased: bool = SetDefaults.on_count_decreased,
    ):
        """Pass."""
        trigger = Schedule.get_trigger(
            query_uuid=query_uuid,
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
        self.triggers = [trigger]

    def get_basic(self, refresh: bool = False) -> SetBasic:
        """Pass."""
        if self.BASIC and not refresh:
            return self.BASIC

        from .. import ApiEndpoints

        api_endpoint = ApiEndpoints.enforcements.get_sets
        request_obj = api_endpoint.load_request(
            filter=f'name == "{self.name}"',
            search=f"{self.name}",
        )
        result = api_endpoint.perform_request(http=self.HTTP, request_obj=request_obj)
        if not result:
            raise NotFoundError(f"Unable to find Enforcement Set with name of {self.name!r}")

        self.BASIC = result[0]
        return self.BASIC

    @staticmethod
    def get_action_obj(name: str, action_type: "ActionType", config: dict) -> dict:
        """Pass."""
        return {
            "name": name,
            "action": {"action_name": action_type.name, "config": config},
        }

    def check_trigger_exists(self, msg: str) -> bool:
        """Pass."""
        if not self._trigger_obj:
            raise NoTriggerDefinedError(
                f"Unable to {msg} - Enforcement Set with Name of {self.name!r}"
                f" and UUID of {self.uuid!r}) has no trigger configured"
            )

    def check_action_category(self, category: Union[ActionCategory, str]) -> ActionCategory:
        """Pass."""
        category = ActionCategory.get_value(category)

        if category.value not in self.actions:
            self.actions[category.value] = []
        return category

    def query_remove(self):
        """Pass."""
        self.check_trigger_exists("remove query")
        self.triggers = []

    def query_update(self, query_uuid: str, query_type: str = SetDefaults.query_type):
        """Pass."""
        if self._trigger_obj:
            self._trigger_obj["view"] = Schedule.get_view(
                query_uuid=query_uuid, query_type=query_type
            )
        else:
            self.set_trigger(query_uuid=query_uuid, query_type=query_type)

    def set_schedule_never(self):
        """Pass."""
        self.check_trigger_exists("set schedule to never")
        self._trigger_obj["period"] = str(Schedule.never)
        self._trigger_obj["period_time"] = self._trigger_obj.get("period_time", Schedule.get_time())
        self._trigger_obj.pop("period_recurrence", None)

    def set_schedule_discovery(self):
        """Pass."""
        self.check_trigger_exists("set schedule to discovery")
        self._trigger_obj["period"] = str(Schedule.discovery)
        self._trigger_obj["period_time"] = self._trigger_obj.get("period_time", Schedule.get_time())
        self._trigger_obj.pop("period_recurrence", None)

    def set_schedule_hourly(self, recurrence: int):
        """Pass."""
        self.check_trigger_exists(f"set schedule to hourly hours {recurrence!r}")
        period_recurrence = Schedule.calc_hourly(value=recurrence)

        self._trigger_obj["period"] = str(Schedule.hourly)
        self._trigger_obj["period_time"] = self._trigger_obj.get("period_time", Schedule.get_time())
        self._trigger_obj["period_recurrence"] = period_recurrence

    def set_schedule_daily(
        self,
        recurrence: int,
        hour: int = SetDefaults.schedule_hour,
        minute: int = SetDefaults.schedule_minute,
    ):
        """Pass."""
        self.check_trigger_exists(
            f"set schedule to daily days {recurrence!r} hour {hour!r} minute {minute!r}"
        )
        period_recurrence = Schedule.calc_daily(value=recurrence)
        period_time = Schedule.get_time(hour=hour, minute=minute)

        self._trigger_obj["period"] = str(Schedule.daily)
        self._trigger_obj["period_time"] = period_time
        self._trigger_obj["period_recurrence"] = period_recurrence

    def set_schedule_weekly(
        self,
        recurrence: Union[str, List[Union[str, int]]],
        hour: int = SetDefaults.schedule_hour,
        minute: int = SetDefaults.schedule_minute,
    ):
        """Pass."""
        self.check_trigger_exists(
            f"set schedule to weekly days {recurrence!r} hour {hour!r} minute {minute!r}"
        )
        period_recurrence = Schedule.calc_weekly(value=recurrence)
        period_time = Schedule.get_time(hour=hour, minute=minute)

        self._trigger_obj["period"] = str(Schedule.weekly)
        self._trigger_obj["period_time"] = period_time
        self._trigger_obj["period_recurrence"] = period_recurrence

    def set_schedule_monthly(
        self,
        recurrence: Union[str, List[int]],
        hour: int = SetDefaults.schedule_hour,
        minute: int = SetDefaults.schedule_minute,
    ):
        """Pass."""
        self.check_trigger_exists(
            f"set schedule to monthly days {recurrence!r} hour {hour!r} minute {minute!r}"
        )
        period_recurrence = Schedule.calc_monthly(value=recurrence)
        period_time = Schedule.get_time(hour=hour, minute=minute)

        self._trigger_obj["period"] = str(Schedule.monthly)
        self._trigger_obj["period_time"] = period_time
        self._trigger_obj["period_recurrence"] = period_recurrence

    def add_action(self, category: str, action: dict):
        """Pass."""
        category = self.check_action_category(category=category)
        self.actions[category.value].append(action)

    def remove_action(self, category: str, name: str):
        """Pass."""
        category = self.check_action_category(category=category)
        matches = [x for x in self.actions[category.value] if x["name"] == name]
        if not matches:
            valids = json_dump(self.actions[category.value])
            raise NotFoundError(
                f"No {category} actions found with name of {name!r}, valids:\n{valids}"
            )

        self.actions[category.value] = [x for x in self.actions[category.value] if x not in matches]

    @property
    def main_action(self) -> dict:
        """Get the main action object."""
        return self.actions["main"]

    @main_action.setter
    def main_action(self, action: dict):
        """Pass."""
        self.actions["main"] = action

    @property
    def failure_actions(self) -> List[dict]:
        """Pass."""
        return self.actions.get(ActionCategory.failure.value) or []

    @property
    def success_actions(self) -> List[dict]:
        """Pass."""
        return self.actions.get(ActionCategory.success.value) or []

    @property
    def post_actions(self) -> List[dict]:
        """Pass."""
        return self.actions.get(ActionCategory.post.value) or []

    @property
    def main_action_str(self) -> str:
        """Pass."""
        return self._get_action_str(value=self.main_action, category="main")

    @property
    def failure_actions_str(self) -> List[str]:
        """Pass."""
        return [
            self._get_action_str(value=x, category=ActionCategory.failure.value, idx=idx)
            for idx, x in enumerate(self.failure_actions)
        ]

    @property
    def success_actions_str(self) -> List[str]:
        """Pass."""
        return [
            self._get_action_str(value=x, category=ActionCategory.success.value, idx=idx)
            for idx, x in enumerate(self.success_actions)
        ]

    @property
    def post_actions_str(self) -> List[str]:
        """Pass."""
        return [
            self._get_action_str(value=x, category=ActionCategory.post.value, idx=idx)
            for idx, x in enumerate(self.post_actions)
        ]

    @property
    def schedule_type(self) -> Optional[str]:
        """Pass."""
        return self._schedule_type.name if self._schedule_type else None

    @property
    def query_type(self) -> Optional[str]:
        """Pass."""
        return self._trigger_view_obj.get("entity", None)

    # BASIC MODEL attribute
    @property
    def query_name(self) -> Optional[str]:
        """Pass."""
        return self.get_basic().query_name

    # BASIC MODEL attribute
    @property
    def triggered_last_date(self) -> Optional[datetime.datetime]:
        """Pass."""
        return self.get_basic().triggered_last_date

    # BASIC MODEL attribute
    @property
    def triggered_count(self) -> Optional[int]:
        """Pass."""
        return self.get_basic().triggered_count

    # BASIC MODEL attribute
    @property
    def schedule(self) -> Optional[str]:
        """Pass."""
        return self.get_basic().schedule

    # BASIC MODEL attribute
    @property
    def updated_date(self) -> datetime.datetime:
        """Pass."""
        return self.get_basic().last_updated

    # BASIC MODEL attribute
    @property
    def updated_user_obj(self) -> dict:
        """Pass."""
        return self.get_basic().updated_user_obj

    # BASIC MODEL attribute
    @property
    def updated_user_name(self) -> str:
        """Get the user name of the user that last updated this set."""
        return self.get_basic().updated_user_name

    # BASIC MODEL attribute
    @property
    def updated_user_source(self) -> str:
        """Get the source of the user that last updated this set."""
        return self.get_basic().updated_user_source

    # BASIC MODEL attribute
    @property
    def updated_user_first_name(self) -> str:
        """Get the first name of the user that last updated this set."""
        return self.get_basic().updated_user_first_name

    # BASIC MODEL attribute
    @property
    def updated_user_last_name(self) -> str:
        """Get the last name of the user that last updated this set."""
        return self.get_basic().updated_user_last_name

    # BASIC MODEL attribute
    @property
    def updated_user_full_name(self) -> str:
        """Get the first and last name of the user that last updated this set."""
        return self.get_basic().updated_user_full_name

    # BASIC MODEL attribute
    @property
    def updated_user(self) -> str:
        """Pass."""
        return self.get_basic().updated_user

    @property
    def only_new_assets(self) -> Optional[bool]:
        """Pass."""
        return OnlyNewAssets.get_bool(value=self._trigger_obj.get("run_on"))

    @only_new_assets.setter
    def only_new_assets(self, value: bool):
        """Pass."""
        self.check_trigger_exists(f"set only_new_assets to {value}")
        self._trigger_obj["run_on"] = OnlyNewAssets.get_str(value)

    @property
    def on_count_above(self) -> Optional[int]:
        """Pass."""
        return self._trigger_conditions_obj.get("above")

    @on_count_above.setter
    def on_count_above(self, value: Optional[int]):
        """Pass."""
        self.check_trigger_exists(f"set on_count_above to {value}")
        self._trigger_obj["conditions"]["above"] = coerce_int(
            obj=value,
            allow_none=True,
            min_value=0,
            errmsg="on_count_above must be an integer above 0 or None",
        )

    @property
    def on_count_below(self) -> Optional[int]:
        """Pass."""
        return self._trigger_conditions_obj.get("below")

    @on_count_below.setter
    def on_count_below(self, value: Optional[int]):
        """Pass."""
        self.check_trigger_exists(f"set on_count_below to {value}")
        self._trigger_obj["conditions"]["below"] = coerce_int(
            obj=value,
            allow_none=True,
            min_value=0,
            errmsg="on_count_below must be an integer above 0 or None",
        )

    @property
    def on_count_increased(self) -> Optional[bool]:
        """Pass."""
        return self._trigger_conditions_obj.get("new_entities")

    @on_count_increased.setter
    def on_count_increased(self, value: bool):
        """Pass."""
        self.check_trigger_exists(f"set on_count_increased to {value}")
        self._trigger_obj["conditions"]["new_entities"] = coerce_bool(
            obj=value, errmsg="on_count_increased must be a boolean"
        )

    @property
    def on_count_decreased(self) -> Optional[bool]:
        """Pass."""
        return self._trigger_conditions_obj.get("previous_entities")

    @on_count_decreased.setter
    def on_count_decreased(self, value: bool):
        """Pass."""
        self.check_trigger_exists(f"set on_count_decreased to {value}")
        self._trigger_obj["conditions"]["previous_entities"] = coerce_bool(
            obj=value, errmsg="on_count_decreased must be a boolean"
        )

    def to_tablize(self):
        """Pass."""
        ident = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            f"Updated Date: {self.updated_date}",
            f"Updated User: {self.updated_user!r}",
        ]
        details = [
            self.main_action_str,
            *self.success_actions_str,
            *self.failure_actions_str,
            *self.post_actions_str,
            f"Query Name: {self.query_name!r}",
            f"Query Type: {self.query_type!r}",
            f"Schedule: {self.schedule}",
            f"Schedule Type: {self.schedule_type}",
            f"Only New Assets: {self.only_new_assets}",
            f"On Count Above: {self.on_count_above}",
            f"On Count Below: {self.on_count_below}",
            f"On Count Increased: {self.on_count_increased}",
            f"On Count Decreased: {self.on_count_decreased}",
            f"Triggered Last Date: {self.triggered_last_date}",
            f"Triggered Count: {self.triggered_count}",
        ]
        return {
            "Identifier": "\n".join(ident),
            "Details": "\n".join(details),
        }

    @staticmethod
    def _get_action_str(value: dict, category: str, idx: Optional[int] = None) -> str:
        """Pass."""
        name = value["name"]
        atype = value["action"]["action_name"]
        pre = f"{category.title()} Action"
        if isinstance(idx, int):
            pre = f"{pre} #{idx +1}"
        return f"{pre} {name!r} ({atype})"

    @property
    def _trigger_conditions_obj(self) -> dict:
        """Pass."""
        return self._trigger_obj.get("conditions", {})

    @property
    def _trigger_view_obj(self) -> dict:
        """Pass."""
        return self._trigger_obj.get("view", {})

    @property
    def _trigger_obj(self) -> dict:
        """Pass."""
        return self.triggers[0] if self.triggers else {}

    @property
    def _trigger_period(self) -> str:
        """Pass."""
        return self._trigger_obj.get("period", "")

    @property
    def _schedule_type(self) -> Optional[Schedule]:
        """Pass."""
        period = self._trigger_obj.get("period", "")
        if period:
            return Schedule.get_value(value=period)
        return None

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            self.main_action_str,
            *self.success_actions_str,
            *self.failure_actions_str,
            *self.post_actions_str,
            f"Query Name: {self.query_name}",
            f"Query Type: {self.query_type}",
            f"Schedule: {self.schedule}",
            f"Schedule Type: {self.schedule_type}",
            f"Only New Assets: {self.only_new_assets}",
            f"On Count Above: {self.on_count_above}",
            f"On Count Below: {self.on_count_below}",
            f"On Count Increased: {self.on_count_increased}",
            f"On Count Decreased: {self.on_count_decreased}",
            f"Triggered Last Date: {self.triggered_last_date}",
            f"Triggered Count: {self.triggered_count}",
            f"Updated Date: {self.updated_date}",
            f"Updated User: {self.updated_user}",
        ]
        return "\n".join(items)

    def __repr__(self):
        """Pass."""
        return self.__str__()

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SetFullSchema


class UpdateRequestSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return UpdateRequest


@dataclasses.dataclass
class UpdateRequest(BaseModel):
    """Pass."""

    id: str
    uuid: str
    name: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return UpdateRequestSchema


class UpdateResponseSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return UpdateResponse


@dataclasses.dataclass
class UpdateResponse(BaseModel):
    """Pass."""

    id: str
    name: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return UpdateResponseSchema

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.id


class DuplicateSchema(BaseSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str()
    name = marshmallow_jsonapi.fields.Str()
    clone_triggers = marshmallow_jsonapi.fields.Bool(load_default=True, dump_default=True)

    class Meta:
        """Pass."""

        type_ = "duplicate_enforcements_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return Duplicate


@dataclasses.dataclass
class Duplicate(BaseModel):
    """Pass."""

    id: str
    uuid: str
    name: str
    clone_triggers: bool = True

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return DuplicateSchema


class CreateSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return Create


@dataclasses.dataclass
class Create(BaseModel):
    """Pass."""

    name: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CreateSchema


class ActionTypeSchema(BaseSchemaJson):
    """Pass."""

    default = marshmallow_jsonapi.fields.Dict(allow_none=True)
    schema = marshmallow_jsonapi.fields.Dict()

    class Meta:
        """Pass."""

        type_ = "actions_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return ActionType


@dataclasses.dataclass
class ActionType(BaseModel):
    """Pass."""

    id: str
    schema: dict
    default: Optional[dict] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return ActionTypeSchema

    def to_tablize(self) -> dict:
        """Pass."""
        return {"Name": self.name, "Config Keys": "\n".join(self.names)}

    @property
    def items(self) -> List[dict]:
        """Pass."""
        return self.schema.get("items", [])

    @property
    def required(self) -> List[str]:
        """Pass."""
        return self.schema.get("required", [])

    @property
    def names(self) -> List[str]:
        """Pass."""
        return [x["name"] for x in self.items]

    @property
    def conditional_schema(self) -> Optional[dict]:
        """Pass."""
        if "conditional" in self.names:
            return [x for x in self.items if x["name"] == "conditional"][0]
        return None

    @property
    def conditional_items(self) -> List[dict]:
        """Pass."""
        schema = self.conditional_schema
        return [x for x in schema["enum"]] if schema else []

    @property
    def conditional_names(self) -> List[str]:
        """Pass."""
        return [x["name"] for x in self.conditional_items]

    @property
    def name(self) -> str:
        """Pass."""
        return self.id

    def get_required_conditionally(self, config: Optional[dict] = None) -> List[str]:
        """Pass."""
        config = {} if config is None else config
        remove_requireds = []
        schema = self.conditional_schema
        if schema and schema["name"] in config:
            key = schema["name"]
            value = config[key]
            remove_requireds = [y for y in self.conditional_names if y != value]
            return [x for x in self.required if x not in remove_requireds]
        return self.required

    def check_config(self, config: Optional[dict] = None) -> dict:
        """Pass."""
        config = {} if config is None else config
        if not isinstance(config, dict):
            raise ApiError(f"Action config must be a dict, not {type(config)}")

        config = self.check_config_unknown(config=config)
        config = self.check_config_missing(config=config)
        return config

    def check_config_missing(self, config: Optional[dict] = None) -> dict:
        """Pass."""
        config = {} if config is None else config
        required = self.get_required_conditionally(config=config)
        missing = [x for x in self.names if x in required and x not in config]

        if missing:
            err = f"Action config missing required items: {missing}"
            raise ConfigRequired("\n\n".join([err, json_dump(self), err]))
        return config

    def check_config_unknown(self, config: Optional[dict] = None) -> dict:
        """Pass."""
        config = {} if config is None else config
        unknowns = [x for x in config if x not in self.names]

        if unknowns:
            err = f"Action config has unknown items: {unknowns}"
            raise ConfigUnknown("\n\n".join([err, json_dump(self), err]))
        return config

    def __str__(self):
        """Pass."""
        return f"name={self.name!r}, config_keys={self.names}"

    def __repr__(self):
        """Pass."""
        return self.__str__()
