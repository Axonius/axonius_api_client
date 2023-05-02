# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi

from ...constants.api import FolderDefaults
from ...constants.ctypes import FolderBase, Refreshables
from ...data import BaseEnum
from ...exceptions import (
    ApiError,
    ConfigRequired,
    ConfigUnknown,
    ConfirmNotTrue,
    NotFoundError,
    NoTriggerDefinedError,
    ToolsError,
)
from ...tools import (
    check_confirm_prompt,
    coerce_bool,
    coerce_int,
    coerce_str_to_csv,
    int_days_map,
    is_str,
    json_dump,
    json_load,
    parse_value_copy,
)
from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm, get_schema_dc
from .generic import Deleted, IntValue, IntValueSchema
from .saved_queries import QueryTypes
from .selection import IdSelection, IdSelectionSchema


class EnforcementDefaults:
    """Pass."""

    query_name: t.Optional[str] = None
    query_type: t.Union["QueryTypes", str] = "devices"
    schedule_type: t.Union["EnforcementSchedule", str] = "never"
    schedule_hour: int = 13
    schedule_minute: int = 0
    schedule_recurrence: t.Optional[t.Union[int, t.List[str]]] = None
    only_new_assets: bool = False
    on_count_above: t.Optional[int] = None
    on_count_below: t.Optional[int] = None
    on_count_increased: bool = False
    on_count_decreased: bool = False


class ActionCategory(BaseEnum):
    """Pass."""

    success: str = "success"
    failure: str = "failure"
    post: str = "post"


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
        cls, value: t.Optional[t.Union["OnlyNewAssets", str]] = all_entities
    ) -> t.Optional[bool]:
        """Pass."""
        if value is not None:
            value = cls.get_value(value=value)

            if value == cls.added_entities:
                return True

            if value == cls.all_entities:
                return False

        return None


class EnforcementSchedule(BaseEnum):
    """Pass."""

    never: str = "never"
    discovery: str = "all"
    hourly: str = "hourly"
    monthly: str = "monthly"
    daily: str = "daily"
    weekly: str = "weekly"

    @classmethod
    def get_value(
        cls, value: t.Union["EnforcementSchedule", str] = EnforcementDefaults.schedule_type
    ) -> "EnforcementSchedule":
        """Pass."""
        return super().get_value(value=value)

    def get_recurrence(self, value: t.Any = EnforcementDefaults.schedule_recurrence) -> t.Any:
        """Pass."""
        return getattr(self, f"calc_{self.name}")(value=value)

    @staticmethod
    def get_time(
        hour: int = EnforcementDefaults.schedule_hour,
        minute: int = EnforcementDefaults.schedule_minute,
    ) -> str:
        """Pass."""
        hour = coerce_int(
            obj=hour,
            min_value=0,
            max_value=23,
            errmsg="EnforcementSchedule time hour value must be an integer between 0 and 23",
        )
        minute = coerce_int(
            obj=minute,
            min_value=0,
            max_value=59,
            errmsg="EnforcementSchedule time minute value must be an integer between 0 and 59",
        )
        return f"{hour:0>2}:{minute:0>2}"

    @staticmethod
    def get_conditions(
        on_count_above: t.Optional[int] = EnforcementDefaults.on_count_above,
        on_count_below: t.Optional[int] = EnforcementDefaults.on_count_below,
        on_count_increased: bool = EnforcementDefaults.on_count_increased,
        on_count_decreased: bool = EnforcementDefaults.on_count_decreased,
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
        query_uuid: t.Optional[str] = None,
        query_type: t.Union[QueryTypes, str] = EnforcementDefaults.query_type,
    ) -> t.Optional[dict]:
        """Pass."""
        query_type = QueryTypes.get_value(query_type)
        if isinstance(query_uuid, str) and query_uuid:
            return {"id": query_uuid, "entity": query_type.value}
        return None

    @classmethod
    def get_trigger(
        cls,
        query_uuid: t.Optional[str] = None,
        query_type: t.Union[QueryTypes, str] = EnforcementDefaults.query_type,
        schedule_type: t.Union["EnforcementSchedule", str] = EnforcementDefaults.schedule_type,
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
    def calc_hourly(value: t.Any = None) -> int:
        """Pass."""
        pre = "EnforcementSchedule Recurrence of 'hourly'"
        err_value = f"{pre} must be an integer between 1 and 24"
        return coerce_int(obj=value, max_value=24, min_value=1, errmsg=err_value)

    @staticmethod
    def calc_monthly(value: t.Any = None) -> t.List[str]:
        """Pass."""
        pre = "EnforcementSchedule Recurrence of 'monthly'"
        err_values = f"{pre} must be a list or CSV of integers between 1 and 29"
        err_value = f"{pre} must be an integer between 1 and 29"

        values = coerce_str_to_csv(value=value, coerce_list=True, errmsg=err_values)
        value = [coerce_int(obj=x, min_value=1, max_value=29, errmsg=err_value) for x in values]
        return [str(x) for x in sorted(list(set(value)))]

    @staticmethod
    def calc_weekly(value: t.Any = None) -> t.List[str]:
        """Pass."""
        pre = "EnforcementSchedule Recurrence of 'weekly'"
        err_value = f"{pre} must be a list or CSV of integers between 0 and 6 or day names"
        try:
            return int_days_map(value=value, names=False)
        except Exception as exc:
            raise ToolsError(f"{err_value}: {exc}")

    @staticmethod
    def calc_daily(value: t.Any = None) -> int:
        """Pass."""
        pre = "EnforcementSchedule Recurrence of 'daily'"
        err_value = f"{pre} must be an integer higher than 1"
        return coerce_int(obj=value, min_value=1, errmsg=err_value)

    @staticmethod
    def calc_never(value: t.Any = None) -> None:
        """Pass."""
        return None

    @staticmethod
    def calc_discovery(value: t.Any = None) -> None:
        """Pass."""
        return None


class EnforcementBasicSchema(BaseSchemaJson):
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
    action_names = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    history = marshmallow.fields.Dict(allow_none=True, load_default={}, dump_default={})
    last_run_status = marshmallow_jsonapi.fields.Str(allow_none=True)
    folder_id = marshmallow_jsonapi.fields.Str(
        load_default=None, dump_default=None, allow_none=True
    )
    next_run = SchemaDatetime(allow_none=True)
    created_by_quick_action = SchemaBool(load_default=False, dump_default=False)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return EnforcementBasicModel

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs):
        """Pass."""
        return {k.replace(".", "_"): v for k, v in data.items()}


class EnforcementFullSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())
    description = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")
    settings = marshmallow_jsonapi.fields.Dict(load_default={}, dump_default={})
    folder_id = marshmallow_jsonapi.fields.Str(
        load_default=None, dump_default=None, allow_none=True
    )
    created_by_quick_action = SchemaBool(load_default=False, dump_default=False)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return EnforcementFullModel


class UpdateDescriptionRequestSchema(BaseSchemaJson):
    """Pass."""

    description = marshmallow_jsonapi.fields.Str()

    class Meta:
        """Pass."""

        type_ = "update_enforcement_description"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return UpdateDescriptionRequestModel


class UpdateEnforcementRequestSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return UpdateEnforcementRequestModel


class MoveEnforcementsRequestSchema(BaseSchemaJson):
    """Pass."""

    folder_id = marshmallow_jsonapi.fields.Str()
    enforcements_ids = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())

    class Meta:
        """Pass."""

        type_ = "update_enforcements_folder_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return MoveEnforcementsRequestModel


class MoveEnforcementsResponseSchema(IntValueSchema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return MoveEnforcementsResponseModel


class UpdateEnforcementResponseSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())
    updated_by = marshmallow_jsonapi.fields.Str(allow_none=True)
    last_updated = SchemaDatetime(allow_none=True)
    last_updated = SchemaDatetime(allow_none=True)
    description = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")
    settings = marshmallow_jsonapi.fields.Dict(load_default={}, dump_default={})
    folder_id = marshmallow_jsonapi.fields.Str(
        load_default=None, dump_default=None, allow_none=True
    )
    created_by_quick_action = SchemaBool(load_default=False, dump_default=False)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return UpdateEnforcementResponseModel


class CopyEnforcementSchema(BaseSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str()
    name = marshmallow_jsonapi.fields.Str()
    clone_triggers = marshmallow_jsonapi.fields.Bool(load_default=True, dump_default=True)

    class Meta:
        """Pass."""

        type_ = "duplicate_enforcements_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return CopyEnforcementModel


class CreateEnforcementSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())
    description = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")

    class Meta:
        """Pass."""

        type_ = "enforcements_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return CreateEnforcementModel


class ActionTypeSchema(BaseSchemaJson):
    """Pass."""

    default = marshmallow_jsonapi.fields.Dict(allow_none=True)
    schema = marshmallow_jsonapi.fields.Dict()
    test_connection = marshmallow_jsonapi.fields.Dict()
    adapter_fields = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())

    class Meta:
        """Pass."""

        type_ = "actions_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ActionType


class RunEnforcementAgainstTriggerRequestSchema(BaseSchemaJson):
    """Pass."""

    ec_page_run = SchemaBool(load_default=False, dump_default=False)
    use_conditions = SchemaBool(load_default=False, dump_default=False)

    class Meta:
        """Pass."""

        type_ = "run_enforcements_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return RunEnforcementAgainstTriggerRequestModel


class RunEnforcementsAgainstTriggerRequestSchema(BaseSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.Nested(IdSelectionSchema)
    use_conditions = SchemaBool(load_default=False, dump_default=False)

    class Meta:
        """Pass."""

        type_ = "run_multiple_enforcements_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return RunEnforcementsAgainstTriggerRequestModel


class Enforcement:
    """Pass."""

    @property
    def folder(self):
        """Pass."""
        return self.HTTP.CLIENT.folders.enforcements.find_cached(folder=self.folder_id)

    @classmethod
    def get_tree_type(cls) -> str:
        """Get the name to use for objects in tree outputs."""
        return "EnforcementSet"

    @property
    def folder_path(self) -> str:
        """Pass."""
        return self.folder.path

    def _check_update_ok(self, reason: str = ""):
        """Pass."""
        return

    def get_names(self) -> t.List[str]:
        """Pass."""
        names: t.List[str] = [x.name for x in self._api.get_sets(full=False)]
        return names

    def move(
        self,
        folder: t.Union[str, FolderBase],
        create: bool = FolderDefaults.create_action,
        refresh: Refreshables = FolderDefaults.refresh_action,
        echo: bool = FolderDefaults.echo_action,
        root: t.Optional[FolderBase] = None,
    ) -> "Enforcement":
        """Move an object to another folder.

        Args:
            folder (t.Union[str, FolderBase]): folder to move an object to
            create (bool, optional): create folder if it does not exist
            refresh (Refreshables, optional): refresh the folders before searching
            echo (bool, optional): echo output to console
            root (t.Optional[FolderBase], optional): root folders to use to find folder
                instead of root folders from `self.folder`
        """
        reason: str = f"Move '{self.folder_path}/@{self.name}' to {folder!r}"
        self._check_update_ok(reason=reason)
        if not isinstance(root, FolderBase):
            root: FolderBase = self.folder.root_folders
            root.refresh(value=refresh)

        folder: FolderBase = root.find(
            folder=folder,
            create=create,
            refresh=False,
            echo=echo,
            minimum_depth=2,
            reason=reason,
        )
        self.folder_id = folder.id
        move_response: MoveEnforcementsResponseModel = self._api._move_sets(
            folder_id=folder.id, enforcements_ids=self.uuid
        )
        updated_obj = self._api.get_set(value=self.uuid)
        updated_obj.move_response = move_response
        return updated_obj

    def copy(
        self,
        folder: t.Optional[t.Union[str, FolderBase]] = None,
        name: t.Optional[str] = None,
        copy_prefix: str = FolderDefaults.copy_prefix,
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo_action,
        refresh: Refreshables = FolderDefaults.refresh_action,
        root: t.Optional[FolderBase] = None,
    ) -> "Enforcement":
        """Create a copy of an object, optionally in a different folder.

        Args:
            folder (t.Optional[t.Union[str, FolderBase]], optional): Folder to copy an object to
            name (t.Optional[str], optional): if supplied, name to give copy, otherwise use
                self.name + copy_prefix
            copy_prefix (str, optional): value to prepend to current name if no new name supplied
            create (bool, optional): create folder if it does not exist
            echo (bool, optional): echo output to console
            refresh (Refreshables, optional): refresh the folders before searching
            root (t.Optional[FolderBase], optional): root folders to use to find folder
                instead of root folders from `self.folder`

        """
        names: t.List[str] = self.get_names()
        name: str = parse_value_copy(
            default=self.name, value=name, copy_prefix=copy_prefix, existing=names
        )
        if not isinstance(root, FolderBase):
            root: FolderBase = self.folder.root_folders
            root.refresh(value=refresh)

        reason: str = f"Copy '{self.folder_path}/@{self.name}' to '{folder}/@{name}'"
        default: FolderBase = None if self.folder.read_only else self.folder
        folder: FolderBase = root.resolve_folder(
            folder=folder,
            create=create,
            refresh=False,
            echo=echo,
            reason=reason,
            default=default,
        )
        full: EnforcementFullModel = self.get_full()
        create_obj: CreateEnforcementModel = CreateEnforcementModel(
            name=name, actions=full.actions, triggers=full.triggers, description=full.description
        )
        create_response_obj: EnforcementFullModel = self._api._create_from_model(
            request_obj=create_obj
        )
        if folder.depth > 1 and folder.id != create_response_obj.folder.id:
            self._api._move_sets(folder_id=folder.id, enforcements_ids=create_response_obj.uuid)
        created_obj = self._api.get_set(value=create_response_obj)
        return created_obj

    @property
    def _api(self) -> object:
        """Pass."""
        return self.HTTP.CLIENT.enforcements

    def delete(
        self,
        confirm: bool = FolderDefaults.confirm,
        echo: bool = FolderDefaults.echo_action,
        prompt: bool = FolderDefaults.prompt,
        prompt_default: bool = FolderDefaults.prompt_default,
    ) -> Deleted:
        """Delete an object.

        Args:
            confirm (bool, optional): if not True, will throw exc
            echo (bool, optional): echo output to console
            prompt (bool, optional): if confirm is not True and this is True, prompt user
                to delete an object
            prompt_default (bool, optional): if prompt is True, default choice to offer user
                in prompt
        """
        reason: str = f"Delete {self.name!r} from {self.folder_path!r}"
        self._check_update_ok(reason=reason)
        check_confirm_prompt(
            reason=reason,
            src=self,
            value=confirm,
            prompt=prompt,
            default=prompt_default,
        )
        return self._api._delete(uuid=self.uuid)

    @property
    def _tree_summary(self) -> dict:
        """Pass."""
        basic, full = self._basic_full
        return {
            "name": basic.name,
            "main_action_name": full.main_action_name,
            "main_action_type": full.main_action_type,
            "query_name": full.query_name,
            "query_type": full.query_type,
            "schedule": full.schedule,
        }

    @property
    def _tree_details(self) -> dict:
        """Pass."""
        basic, full = self._basic_full
        return {
            "name": basic.name,
            "uuid": basic.uuid,
            "description": full.description,
            "main_action_name": full.main_action_name,
            "main_action_type": full.main_action_type,
            "query_name": full.query_name,
            "query_type": full.query_type,
            "schedule": full.schedule,
            "updated_by": basic.updated_by_str,
            "last_updated": basic.last_updated_str,
            "last_run_status": basic.last_run_status,
            "next_run": str(basic.next_run),
        }

    @property
    def _basic_full(self) -> t.Tuple[t.Type[BaseModel], t.Type[BaseModel]]:
        """Pass."""
        if isinstance(self, EnforcementBasic):
            return self, self.get_full()
        elif isinstance(self, EnforcementFull):
            return self.get_basic(), self
        else:
            raise ApiError(f"Unexpected type {type(self)}")

    def get_tree_entry(self, include_details: bool = False) -> str:
        """Pass."""

        def to_str(value):
            return str(value) if isinstance(value, datetime.datetime) else value

        obj: dict = self._tree_details if include_details else self._tree_summary
        items: t.List[str] = [f"{k}={to_str(v)!r}" for k, v in obj.items()]
        items: str = ", ".join(items)
        return f"{self.get_tree_type()}({items})"


class EnforcementBasic(Enforcement):
    """Pass."""

    FULL: t.ClassVar["EnforcementFullModel"] = None

    @property
    def description(self) -> str:
        """Pass."""
        return self.get_full().description

    def get_basic(self, refresh: bool = False) -> "EnforcementBasicModel":
        """Pass."""
        if not refresh:
            return self

        result: t.List[EnforcementBasicModel] = self._api._get_sets(
            filter=f'name == "{self.name}"',
            search=f"{self.name}",
        )
        if not result:
            raise NotFoundError(f"Unable to find Enforcement Set with name of {self.name!r}")

        return result[0]

    def get_full(self, refresh: bool = False) -> "EnforcementFullModel":
        """Pass."""
        if self.FULL and not refresh:
            return self.FULL

        self.FULL: EnforcementFullModel = self._api._get_set(uuid=self.uuid)
        self.FULL.BASIC = self
        return self.FULL

    def update_description(self, value: str, append: bool = False) -> "EnforcementBasicModel":
        """Pass."""
        return self.get_full().update_description(value=value, append=append)

    @property
    def updated_by_str(self) -> str:
        """Pass."""
        from .system_users import SystemUser

        return SystemUser.get_user_source(value=self.updated_by)

    @property
    def last_updated_str(self) -> str:
        """Get the last updated in str format."""
        return (
            self.last_updated.strftime("%Y-%m-%dT%H:%M:%S%z")
            if isinstance(self.last_updated, datetime.datetime)
            else self.last_updated
        )

    @property
    def query_name(self) -> t.Optional[str]:
        """Pass."""
        return self.triggers_view_name or None

    @property
    def triggered_last_date(self) -> t.Optional[datetime.datetime]:
        """Pass."""
        return self.last_triggered

    @property
    def triggered_count(self) -> t.Optional[int]:
        """Pass."""
        return self.triggers_times_triggered

    @property
    def schedule(self) -> t.Optional[str]:
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
        """Get the username of the user that last updated this set."""
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

    def delete(self, confirm: bool = False) -> Deleted:
        """Pass."""
        if confirm is True:
            return self._api._delete(uuid=self.uuid)
        raise ConfirmNotTrue(f"Confirm is {confirm}, not {True} - can not delete {self}")

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            f"Folder: {self.folder_path!r}",
            f"Description: {self.description!r}",
            self.main_action_str,
            f"Query Name: {self.query_name}",
            f"EnforcementSchedule: {self.schedule}",
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
            f"Folder: {self.folder_path!r}",
            f"Description: {self.description!r}",
        ]
        details = [
            self.main_action_str,
            f"Query Name: {self.query_name!r}",
            f"EnforcementSchedule: {self.schedule}",
            f"Triggered Last Date: {self.triggered_last_date}",
            f"Triggered Count: {self.triggered_count}",
            f"Updated Date: {self.updated_date}",
            f"Updated User: {self.updated_user!r}",
        ]
        return {
            "Identifier": "\n".join(ident),
            "Details": "\n".join(details),
        }

    def __repr__(self):
        """Pass."""
        return self.__str__()


class EnforcementFull(Enforcement):
    """Pass."""

    BASIC: t.ClassVar["EnforcementBasicModel"] = None

    def set_trigger(
        self,
        query_uuid: t.Optional[str] = None,
        query_type: str = EnforcementDefaults.query_type,
        schedule_type: t.Union["EnforcementSchedule", str] = EnforcementDefaults.schedule_type,
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
    ):
        """Pass."""
        trigger = EnforcementSchedule.get_trigger(
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

    def update_description(self, value: str, append: bool = False) -> "EnforcementBasicModel":
        """Pass."""
        if append and is_str(self.description):
            value = f"{self.description} {value}"

        self.description = value
        response = self._api._update_description(uuid=self.uuid, description=value)
        return response

    @property
    def main_action_name(self) -> str:
        """Pass."""
        return self.main_action["name"]

    @property
    def main_action_type(self) -> str:
        """Pass."""
        return self.main_action["action"]["action_name"]

    def get_basic(self, refresh: bool = False) -> "EnforcementBasicModel":
        """Pass."""
        if self.BASIC and not refresh:
            return self.BASIC

        result: t.List[EnforcementBasicModel] = self._api._get_sets(
            filter=f'name == "{self.name}"',
            search=f"{self.name}",
        )
        if not result:
            raise NotFoundError(f"Unable to find Enforcement Set with name of {self.name!r}")

        self.BASIC: EnforcementBasicModel = result[0]
        self.BASIC.FULL = self
        return self.BASIC

    def get_full(self, refresh: bool = False) -> "EnforcementFullModel":
        """Pass."""
        if not refresh:
            return self

        return self._api._get_set(uuid=self.uuid)

    @staticmethod
    def get_action_obj(name: str, action_type: "ActionType", config: dict) -> dict:
        """Pass."""
        return {
            "name": name,
            "action": {"action_name": action_type.name, "config": config},
        }

    def check_trigger_exists(self, msg: str, error: bool = True) -> bool:
        """Pass."""
        if not self.has_trigger:
            err = (
                f"Unable to {msg} - Enforcement Set with Name of {self.name!r}"
                f" and UUID of {self.uuid!r} has no trigger configured"
            )
            if error:
                raise NoTriggerDefinedError(f"{self}\n{err}")
            else:
                self.logger.warning(err)
        return self.has_trigger

    @property
    def has_trigger(self) -> bool:
        """Pass."""
        return bool(self._trigger_obj)

    def check_action_category(self, category: t.Union[ActionCategory, str]) -> ActionCategory:
        """Pass."""
        category = ActionCategory.get_value(category)

        if category.value not in self.actions:
            self.actions[category.value] = []
        return category

    def query_remove(self):
        """Pass."""
        self.check_trigger_exists("remove query")
        self.triggers = []

    def query_update(self, query_uuid: str, query_type: str = EnforcementDefaults.query_type):
        """Pass."""
        if self._trigger_obj:
            self._trigger_obj["view"] = EnforcementSchedule.get_view(
                query_uuid=query_uuid, query_type=query_type
            )
        else:
            self.set_trigger(query_uuid=query_uuid, query_type=query_type)

    def set_schedule_never(self):
        """Pass."""
        self.check_trigger_exists("set schedule to never")
        self._trigger_obj["period"] = str(EnforcementSchedule.never)
        self._trigger_obj["period_time"] = self._trigger_obj.get(
            "period_time", EnforcementSchedule.get_time()
        )
        self._trigger_obj.pop("period_recurrence", None)

    def set_schedule_discovery(self):
        """Pass."""
        self.check_trigger_exists("set schedule to discovery")
        self._trigger_obj["period"] = str(EnforcementSchedule.discovery)
        self._trigger_obj["period_time"] = self._trigger_obj.get(
            "period_time", EnforcementSchedule.get_time()
        )
        self._trigger_obj.pop("period_recurrence", None)

    def set_schedule_hourly(self, recurrence: int):
        """Pass."""
        self.check_trigger_exists(f"set schedule to hourly hours {recurrence!r}")
        period_recurrence = EnforcementSchedule.calc_hourly(value=recurrence)

        self._trigger_obj["period"] = str(EnforcementSchedule.hourly)
        self._trigger_obj["period_time"] = self._trigger_obj.get(
            "period_time", EnforcementSchedule.get_time()
        )
        self._trigger_obj["period_recurrence"] = period_recurrence

    def set_schedule_daily(
        self,
        recurrence: int,
        hour: int = EnforcementDefaults.schedule_hour,
        minute: int = EnforcementDefaults.schedule_minute,
    ):
        """Pass."""
        self.check_trigger_exists(
            f"set schedule to daily days {recurrence!r} hour {hour!r} minute {minute!r}"
        )
        period_recurrence = EnforcementSchedule.calc_daily(value=recurrence)
        period_time = EnforcementSchedule.get_time(hour=hour, minute=minute)

        self._trigger_obj["period"] = str(EnforcementSchedule.daily)
        self._trigger_obj["period_time"] = period_time
        self._trigger_obj["period_recurrence"] = period_recurrence

    def set_schedule_weekly(
        self,
        recurrence: t.Union[str, t.List[t.Union[str, int]]],
        hour: int = EnforcementDefaults.schedule_hour,
        minute: int = EnforcementDefaults.schedule_minute,
    ):
        """Pass."""
        self.check_trigger_exists(
            f"set schedule to weekly days {recurrence!r} hour {hour!r} minute {minute!r}"
        )
        period_recurrence = EnforcementSchedule.calc_weekly(value=recurrence)
        period_time = EnforcementSchedule.get_time(hour=hour, minute=minute)

        self._trigger_obj["period"] = str(EnforcementSchedule.weekly)
        self._trigger_obj["period_time"] = period_time
        self._trigger_obj["period_recurrence"] = period_recurrence

    def set_schedule_monthly(
        self,
        recurrence: t.Union[str, t.List[int]],
        hour: int = EnforcementDefaults.schedule_hour,
        minute: int = EnforcementDefaults.schedule_minute,
    ):
        """Pass."""
        self.check_trigger_exists(
            f"set schedule to monthly days {recurrence!r} hour {hour!r} minute {minute!r}"
        )
        period_recurrence = EnforcementSchedule.calc_monthly(value=recurrence)
        period_time = EnforcementSchedule.get_time(hour=hour, minute=minute)

        self._trigger_obj["period"] = str(EnforcementSchedule.monthly)
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
    def failure_actions(self) -> t.List[dict]:
        """Pass."""
        return self.actions.get(ActionCategory.failure.value) or []

    @property
    def success_actions(self) -> t.List[dict]:
        """Pass."""
        return self.actions.get(ActionCategory.success.value) or []

    @property
    def post_actions(self) -> t.List[dict]:
        """Pass."""
        return self.actions.get(ActionCategory.post.value) or []

    @property
    def main_action_str(self) -> str:
        """Pass."""
        return self._get_action_str(value=self.main_action, category="main")

    @property
    def failure_actions_str(self) -> t.List[str]:
        """Pass."""
        return [
            self._get_action_str(value=x, category=ActionCategory.failure.value, idx=idx)
            for idx, x in enumerate(self.failure_actions)
        ]

    @property
    def success_actions_str(self) -> t.List[str]:
        """Pass."""
        return [
            self._get_action_str(value=x, category=ActionCategory.success.value, idx=idx)
            for idx, x in enumerate(self.success_actions)
        ]

    @property
    def post_actions_str(self) -> t.List[str]:
        """Pass."""
        return [
            self._get_action_str(value=x, category=ActionCategory.post.value, idx=idx)
            for idx, x in enumerate(self.post_actions)
        ]

    @property
    def schedule_type(self) -> t.Optional[str]:
        """Pass."""
        return self._schedule_type.name if self._schedule_type else None

    @property
    def query_type(self) -> t.Optional[str]:
        """Pass."""
        return self._trigger_view_obj.get("entity", None)

    # BASIC MODEL attribute
    @property
    def query_name(self) -> t.Optional[str]:
        """Pass."""
        return self.get_basic().query_name

    # BASIC MODEL attribute
    @property
    def triggered_last_date(self) -> t.Optional[datetime.datetime]:
        """Pass."""
        return self.get_basic().triggered_last_date

    # BASIC MODEL attribute
    @property
    def triggered_count(self) -> t.Optional[int]:
        """Pass."""
        return self.get_basic().triggered_count

    # BASIC MODEL attribute
    @property
    def schedule(self) -> t.Optional[str]:
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
        """Get the username of the user that last updated this set."""
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
    def only_new_assets(self) -> t.Optional[bool]:
        """Pass."""
        return OnlyNewAssets.get_bool(value=self._trigger_obj.get("run_on"))

    @only_new_assets.setter
    def only_new_assets(self, value: bool):
        """Pass."""
        self.check_trigger_exists(f"set only_new_assets to {value}")
        self._trigger_obj["run_on"] = OnlyNewAssets.get_str(value)

    @property
    def on_count_above(self) -> t.Optional[int]:
        """Pass."""
        return self._trigger_conditions_obj.get("above")

    @on_count_above.setter
    def on_count_above(self, value: t.Optional[int]):
        """Pass."""
        self.check_trigger_exists(f"set on_count_above to {value}")
        self._trigger_obj["conditions"]["above"] = coerce_int(
            obj=value,
            allow_none=True,
            min_value=0,
            errmsg="on_count_above must be an integer above 0 or None",
        )

    @property
    def on_count_below(self) -> t.Optional[int]:
        """Pass."""
        return self._trigger_conditions_obj.get("below")

    @on_count_below.setter
    def on_count_below(self, value: t.Optional[int]):
        """Pass."""
        self.check_trigger_exists(f"set on_count_below to {value}")
        self._trigger_obj["conditions"]["below"] = coerce_int(
            obj=value,
            allow_none=True,
            min_value=0,
            errmsg="on_count_below must be an integer above 0 or None",
        )

    @property
    def on_count_increased(self) -> t.Optional[bool]:
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
    def on_count_decreased(self) -> t.Optional[bool]:
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
            f"Folder: {self.folder_path!r}",
            f"Description: {self.description!r}",
        ]
        details = [
            self.main_action_str,
            *self.success_actions_str,
            *self.failure_actions_str,
            *self.post_actions_str,
            f"Query Name: {self.query_name!r}",
            f"Query Type: {self.query_type!r}",
            f"EnforcementSchedule: {self.schedule}",
            f"EnforcementSchedule Type: {self.schedule_type}",
            f"Only New Assets: {self.only_new_assets}",
            f"On Count Above: {self.on_count_above}",
            f"On Count Below: {self.on_count_below}",
            f"On Count Increased: {self.on_count_increased}",
            f"On Count Decreased: {self.on_count_decreased}",
            f"Triggered Last Date: {self.triggered_last_date}",
            f"Triggered Count: {self.triggered_count}",
            f"Updated Date: {self.updated_date}",
            f"Updated User: {self.updated_user!r}",
        ]
        return {
            "Identifier": "\n".join(ident),
            "Details": "\n".join(details),
        }

    @staticmethod
    def _get_action_str(value: dict, category: str, idx: t.Optional[int] = None) -> str:
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
    def _schedule_type(self) -> t.Optional[EnforcementSchedule]:
        """Pass."""
        period = self._trigger_obj.get("period", "")
        if period:
            return EnforcementSchedule.get_value(value=period)
        return None

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            f"Folder: {self.folder_path!r}",
            f"Description: {self.description!r}",
            self.main_action_str,
            *self.success_actions_str,
            *self.failure_actions_str,
            *self.post_actions_str,
            f"Query Name: {self.query_name}",
            f"Query Type: {self.query_type}",
            f"EnforcementSchedule: {self.schedule}",
            f"EnforcementSchedule Type: {self.schedule_type}",
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


@dataclasses.dataclass(repr=False)
class EnforcementBasicModel(BaseModel, EnforcementBasic):
    """Pass."""

    id: str
    uuid: str
    name: str

    actions_main: str
    actions_main_name: str
    actions_main_type: str

    triggers_period: t.Optional[str] = None
    triggers_view_name: t.Optional[str] = None
    triggers_last_triggered: t.Optional[str] = None
    triggers_times_triggered: t.Optional[int] = None

    updated_by: t.Optional[str] = None
    last_updated: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True, load_default=None, dump_default=None), default=None
    )
    last_triggered: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True, load_default=None, dump_default=None), default=None
    )
    action_names: t.Optional[t.List[str]] = dataclasses.field(default_factory=list)
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)
    history: t.Optional[dict] = dataclasses.field(default_factory=dict)
    last_run_status: t.Optional[str] = None
    folder_id: t.Optional[str] = None
    next_run: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True, load_default=None, dump_default=None), default=None
    )
    created_by_quick_action: t.Optional[bool] = False
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return EnforcementBasicSchema


@dataclasses.dataclass
class EnforcementFullModel(BaseModel, EnforcementFull):
    """Pass."""

    id: str
    uuid: str
    name: str
    actions: dict
    triggers: t.List[dict]
    description: t.Optional[str] = ""
    settings: t.Optional[dict] = dataclasses.field(default_factory=dict)
    folder_id: t.Optional[str] = None
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)
    created_by_quick_action: t.Optional[bool] = False

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return EnforcementFullSchema

    @property
    def main(self):
        """Pass."""
        return self.main_action


@dataclasses.dataclass
class UpdateDescriptionRequestModel(BaseModel):
    """Pass."""

    description: str

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return UpdateDescriptionRequestSchema


@dataclasses.dataclass
class UpdateEnforcementRequestModel(BaseModel):
    """Pass."""

    id: str
    uuid: str
    name: str
    actions: dict
    triggers: t.List[dict]

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return UpdateEnforcementRequestSchema


@dataclasses.dataclass
class MoveEnforcementsRequestModel(BaseModel):
    """Pass."""

    folder_id: str
    enforcements_ids: t.List[str]

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return MoveEnforcementsRequestSchema


@dataclasses.dataclass
class MoveEnforcementsResponseModel(IntValue):
    """Pass."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return MoveEnforcementsResponseSchema


@dataclasses.dataclass
class UpdateEnforcementResponseModel(BaseModel):
    """Pass."""

    id: str
    name: str
    actions: dict
    triggers: t.List[dict]
    updated_by: t.Optional[str] = None
    last_updated: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True, load_default=None, dump_default=None), default=None
    )
    description: t.Optional[str] = ""
    folder_id: t.Optional[str] = None
    settings: t.Optional[dict] = dataclasses.field(default_factory=dict)
    created_by_quick_action: t.Optional[bool] = False
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        if not is_str(self.description):
            self.description = ""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return UpdateEnforcementResponseSchema

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.id


@dataclasses.dataclass
class CopyEnforcementModel(BaseModel):
    """Pass."""

    id: str
    uuid: str
    name: str
    clone_triggers: bool = True

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CopyEnforcementSchema


@dataclasses.dataclass
class CreateEnforcementModel(BaseModel):
    """Pass."""

    name: str
    actions: dict
    triggers: t.List[dict]
    description: t.Optional[str] = ""

    def __post_init__(self):
        """Pass."""
        if not is_str(self.description):
            self.description = ""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CreateEnforcementSchema


@dataclasses.dataclass
class ActionType(BaseModel):
    """Pass."""

    id: str
    schema: dict
    default: t.Optional[dict] = None
    test_connection: t.Optional[dict] = dataclasses.field(default_factory=dict)
    adapter_fields: t.Optional[t.List[str]] = dataclasses.field(default_factory=list)
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ActionTypeSchema

    def to_tablize(self) -> dict:
        """Pass."""
        return {"Name": self.name, "Config Keys": "\n".join(self.names)}

    @property
    def items(self) -> t.List[dict]:
        """Pass."""
        return self.schema.get("items", [])

    @property
    def required(self) -> t.List[str]:
        """Pass."""
        return self.schema.get("required", [])

    @property
    def names(self) -> t.List[str]:
        """Pass."""
        return [x["name"] for x in self.items]

    @property
    def conditional_schema(self) -> t.Optional[dict]:
        """Pass."""
        if "conditional" in self.names:
            return [x for x in self.items if x["name"] == "conditional"][0]
        return None

    @property
    def conditional_items(self) -> t.List[dict]:
        """Pass."""
        schema = self.conditional_schema
        return [x for x in schema["enum"]] if schema else []

    @property
    def conditional_names(self) -> t.List[str]:
        """Pass."""
        return [x["name"] for x in self.conditional_items]

    @property
    def name(self) -> str:
        """Pass."""
        return self.id

    def get_required_conditionally(self, config: t.Optional[dict] = None) -> t.List[str]:
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

    def check_config(self, config: t.Optional[dict] = None) -> dict:
        """Pass."""
        config = {} if config is None else config
        if not isinstance(config, dict):
            raise ApiError(f"Action config must be a dict, not {type(config)}")

        config = self.check_config_unknown(config=config)
        config = self.check_config_missing(config=config)
        return config

    def check_config_missing(self, config: t.Optional[dict] = None) -> dict:
        """Pass."""
        config = {} if config is None else config
        required = self.get_required_conditionally(config=config)
        missing = [x for x in self.names if x in required and x not in config]

        if missing:
            err = f"Action config missing required items: {missing}"
            raise ConfigRequired("\n\n".join([err, json_dump(self), err]))
        return config

    def check_config_unknown(self, config: t.Optional[dict] = None) -> dict:
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


@dataclasses.dataclass
class RunEnforcementAgainstTriggerRequestModel(BaseModel):
    """Pass."""

    ec_page_run: bool = get_schema_dc(
        schema=RunEnforcementAgainstTriggerRequestSchema,
        key="ec_page_run",
        default=False,
    )
    use_conditions: bool = get_schema_dc(
        schema=RunEnforcementAgainstTriggerRequestSchema,
        key="use_conditions",
        default=False,
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return RunEnforcementAgainstTriggerRequestSchema


@dataclasses.dataclass
class RunEnforcementsAgainstTriggerRequestModel(BaseModel):
    """Pass."""

    value: IdSelection = get_schema_dc(
        schema=RunEnforcementsAgainstTriggerRequestSchema,
        key="value",
    )
    use_conditions: bool = get_schema_dc(
        schema=RunEnforcementsAgainstTriggerRequestSchema,
        key="use_conditions",
        default=False,
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return RunEnforcementsAgainstTriggerRequestSchema
