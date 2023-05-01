# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, field_from_mm
from .task_full import TaskFull


class TaskBasicSchema(BaseSchemaJson):
    """Schema for enforcement task in basic model."""

    id = mm_fields.Str(data_key="id", description="The task id", required=True)
    uuid = mm_fields.Str(data_key="uuid", description="The task id", required=True)
    pretty_id = mm_fields.Str(
        data_key="pretty_id", description="The ID of the task in the UI", required=True
    )
    date_fetched = mm_fields.Str(
        data_key="date_fetched", description="The date when the task was created", required=True
    )
    enforcement_name = mm_fields.Str(
        data_key="enforcement_name",
        description="The enforcement set name",
        required=True,
    )
    result_main_action_action_name = mm_fields.Str(
        data_key="result_main_action_action_name",
        description="The action type",
        required=True,
    )
    result_metadata_task_name = mm_fields.Str(
        data_key="result_metadata_task_name",
        description="The action name",
        required=True,
    )
    result_main_name = mm_fields.Str(
        data_key="result_main_name",
        description="The task name",
        required=True,
    )

    affected_assets = mm_fields.Int(
        data_key="affected_assets",
        description="Total amount of affected assets by task",
        allow_none=True,
        load_default=None,
    )
    success_count = mm_fields.Int(
        data_key="success_count",
        description="Amount of assets succeeded in the main action",
        allow_none=True,
        load_default=None,
    )
    failure_count = mm_fields.Int(
        data_key="failure_count",
        description="Amount of assets failed in the main " "action",
        allow_none=True,
        load_default=None,
    )
    result_metadata_successful_total = mm_fields.Str(
        data_key="result_metadata_successful_total",
        description="The numbers of successful tasks / all tasks",
        allow_none=True,
        load_default=None,
    )

    module = mm_fields.Str(
        data_key="module",
        description="The asset type of the query used",
        allow_none=True,
        load_default=None,
    )
    result_metadata_trigger_view_name = mm_fields.Str(
        data_key="result_metadata_trigger_view_name",
        description="The name of the query defined as the enforcement set trigger",
        allow_none=True,
        load_default=None,
    )

    aggregated_status = mm_fields.Str(
        data_key="aggregated_status",
        description="The aggregated status of task",
        allow_none=True,
        load_default=None,
    )
    result_metadata_status = mm_fields.Str(
        data_key="result_metadata_status",
        description="The status of the task",
        allow_none=True,
        load_default=None,
    )

    scheduling = mm_fields.Str(
        data_key="scheduling",
        description="The task run scheduling",
        allow_none=True,
        load_default=None,
    )
    duration = mm_fields.Str(
        data_key="duration",
        description="The task run duration, in HH:mm:ss.SS format",
        allow_none=True,
        load_default=None,
    )
    result_metadata_trigger_condition = mm_fields.Str(
        data_key="result_metadata_trigger_condition",
        description="The condition which triggered the run",
        allow_none=True,
        load_default=None,
    )
    discovery_id = mm_fields.Str(
        data_key="discovery_id",
        description="The ID of the discovery cycle that originated the set run record",
        allow_none=True,
        load_default=None,
    )
    finished_at = SchemaDatetime(
        data_key="finished_at",
        description="The timestamp when task finished running",
        allow_none=True,
        load_default=None,
    )
    started_at = SchemaDatetime(
        data_key="started_at",
        description="The timestamp when task started running",
        allow_none=True,
        load_default=None,
    )

    action_names = mm_fields.List(
        mm_fields.Str(),
        data_key="action_names",
        description="List of names for all actions in task.",
        load_default=list,
    )
    actions_details = mm_fields.Dict(
        data_key="actions_details",
        description="The details of all actions contained in the task.",
        load_default=dict,
    )

    class Meta:
        """Marshmallow JSONAPI metaclass."""

        type_: str = "tasks_schema"
        self_url: str = "/api/tasks/{id}"
        self_url_kwargs: t.Dict[str, str] = {"id": "<id>"}
        self_url_many: str = "/api/tasks"
        unknown: str = marshmallow.INCLUDE

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return TaskBasic

    @marshmallow.pre_load
    def _fix_names(self, data: dict, **kwargs) -> dict:
        """Replace dots with underscores in field names.

        Args:
            **kwargs (object):
                Marshmallow kwargs
            data (dict):
                Marshmallow data to be preloaded

        Returns:
            dict: data with dots replaced with underscores
        """
        fix_find: str = kwargs.get("fix_find", ".")
        fix_replace: str = kwargs.get("fix_replace", "_")
        return {k.replace(fix_find, fix_replace): v for k, v in data.items()}


SCHEMA: marshmallow.Schema = TaskBasicSchema()


@dataclasses.dataclass()
class TaskBasic(BaseModel):
    """Model for getting enforcement tasks in basic model."""

    id: str = field_from_mm(SCHEMA, "id")
    uuid: str = field_from_mm(SCHEMA, "uuid")
    pretty_id: str = field_from_mm(SCHEMA, "pretty_id")
    date_fetched: str = field_from_mm(SCHEMA, "date_fetched")
    enforcement_name: str = field_from_mm(SCHEMA, "enforcement_name")
    result_main_action_action_name: str = field_from_mm(SCHEMA, "result_main_action_action_name")
    result_metadata_task_name: str = field_from_mm(SCHEMA, "result_metadata_task_name")
    result_main_name: str = field_from_mm(SCHEMA, "result_main_name")

    affected_assets: int = field_from_mm(SCHEMA, "affected_assets")
    success_count: int = field_from_mm(SCHEMA, "success_count")
    failure_count: int = field_from_mm(SCHEMA, "failure_count")
    result_metadata_successful_total: str = field_from_mm(
        SCHEMA, "result_metadata_successful_total"
    )

    module: t.Optional[str] = field_from_mm(SCHEMA, "module")
    result_metadata_trigger_view_name: t.Optional[str] = field_from_mm(
        SCHEMA, "result_metadata_trigger_view_name"
    )

    aggregated_status: t.Optional[str] = field_from_mm(SCHEMA, "aggregated_status")
    result_metadata_status: t.Optional[str] = field_from_mm(SCHEMA, "result_metadata_status")

    scheduling: t.Optional[str] = field_from_mm(SCHEMA, "scheduling")
    duration: t.Optional[str] = field_from_mm(SCHEMA, "duration")
    result_metadata_trigger_condition: t.Optional[str] = field_from_mm(
        SCHEMA, "result_metadata_trigger_condition"
    )
    discovery_id: t.Optional[str] = field_from_mm(SCHEMA, "discovery_id")
    finished_at: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "finished_at")
    started_at: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "started_at")

    action_names: t.List[str] = field_from_mm(SCHEMA, "action_names")
    actions_details: dict = field_from_mm(SCHEMA, "actions_details")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return TaskBasicSchema

    def get_full(self) -> "TaskFull":
        """Pass."""
        # TODO: ensure cached!
        # noinspection PyUnresolvedReferences
        return self.HTTP.CLIENT.enforcements.tasks.get_full(uuid=self.uuid)
