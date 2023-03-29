# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t
from datetime import datetime

import marshmallow

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, get_schema_dc
from .task_full import TaskFull


class TaskBasicSchema(BaseSchemaJson):
    """Schema for enforcement task in basic model."""

    id = marshmallow.fields.Str()
    uuid = marshmallow.fields.Str(
        description="The task id",
    )
    date_fetched = marshmallow.fields.Str(
        description="The date when the task was created",
    )
    enforcement_name = marshmallow.fields.Str(
        description="The enforcement set name",
    )
    aggregated_status = marshmallow.fields.Str(
        description="The aggregated status of task",
    )
    pretty_id = marshmallow.fields.Str(
        description="The task pretty id.",
    )
    affected_assets = marshmallow.fields.Integer(
        description="Total amount of affected assets by task",
    )
    success_count = marshmallow.fields.Integer(
        description="Amount of assets succeeded in the main action",
    )
    failure_count = marshmallow.fields.Integer(
        description="Amount of assets failed in the main action",
    )
    module = marshmallow.fields.Str(
        description="The asset type of the query used",
    )
    scheduling = marshmallow.fields.Str(
        description="The task run scheduling",
    )
    discovery_id = marshmallow.fields.Str(
        description="The ID of the discovery cycle that originated the set run record",
        allow_none=True,
    )
    duration = marshmallow.fields.Str(
        description="The task run duration, in HH:mm:ss.SS format",
    )
    actions_details = marshmallow.fields.Dict(
        description="The details of all actions contained in the task.",
    )
    action_names = marshmallow.fields.List(
        marshmallow.fields.Str(),
        description="List of names for all actions in task.",
    )
    result_main_action_action_name = marshmallow.fields.Str(
        description="The action type",
    )
    result_main_name = marshmallow.fields.Str(
        description="The task name",
    )
    result_metadata_status = marshmallow.fields.Str(
        description="The status of the task",
    )
    result_metadata_successful_total = marshmallow.fields.Str(
        description="The numbers of successful tasks / all tasks",
    )
    result_metadata_trigger_condition = marshmallow.fields.Str(
        description="The condition which triggered the run",
    )
    result_metadata_task_name = marshmallow.fields.Str(
        description="The action name",
    )
    result_metadata_trigger_view_name = marshmallow.fields.Str(
        description="The name of the query defined as the enforcement set trigger",
    )
    finished_at = SchemaDatetime(
        description="The timestamp when task finished running",
        allow_none=True,
    )
    started_at = SchemaDatetime(
        description="The timestamp when task started running",
        allow_none=True,
    )

    @marshmallow.pre_load
    def _rename_dots(self, data: dict, **kwargs) -> dict:
        """Replace dots with underscores in field names."""
        return {k.replace(".", "_"): v for k, v in data.items()}

    class Meta:
        """Marshmallow JSONAPI meta class."""

        type_ = "tasks_schema"
        self_url = "/api/tasks/{id}"
        self_url_kwargs = {"id": "<id>"}
        self_url_many = "/api/tasks"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return TaskBasic


@dataclasses.dataclass()
class TaskBasic(BaseModel):
    """Model for getting enforcement tasks in basic model."""

    id: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="id",
    )
    uuid: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="uuid",
    )
    enforcement_name: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="enforcement_name",
    )
    date_fetched: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="date_fetched",
    )
    aggregated_status: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="aggregated_status",
    )
    pretty_id: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="pretty_id",
    )
    affected_assets: int = get_schema_dc(
        schema=TaskBasicSchema,
        key="affected_assets",
    )
    success_count: int = get_schema_dc(
        schema=TaskBasicSchema,
        key="success_count",
    )
    failure_count: int = get_schema_dc(
        schema=TaskBasicSchema,
        key="failure_count",
    )
    module: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="module",
    )
    scheduling: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="scheduling",
    )
    duration: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="duration",
    )
    action_names: t.List[str] = get_schema_dc(
        schema=TaskBasicSchema,
        key="action_names",
    )
    actions_details: dict = get_schema_dc(
        schema=TaskBasicSchema,
        key="actions_details",
    )
    result_main_action_action_name: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="result_main_action_action_name",
    )
    result_main_name: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="result_main_name",
    )
    result_metadata_status: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="result_metadata_status",
    )
    result_metadata_successful_total: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="result_metadata_successful_total",
    )
    result_metadata_task_name: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="result_metadata_task_name",
    )
    result_metadata_trigger_condition: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="result_metadata_trigger_condition",
    )
    result_metadata_trigger_view_name: str = get_schema_dc(
        schema=TaskBasicSchema,
        key="result_metadata_trigger_view_name",
    )
    discovery_id: t.Optional[str] = get_schema_dc(
        schema=TaskBasicSchema,
        key="discovery_id",
        default=None,
    )
    finished_at: t.Optional[datetime] = get_schema_dc(
        schema=TaskBasicSchema,
        key="finished_at",
        default=None,
    )
    started_at: t.Optional[datetime] = get_schema_dc(
        schema=TaskBasicSchema,
        key="started_at",
        default=None,
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return TaskBasicSchema

    def get_full(self) -> "TaskFull":
        """Pass."""
        return self.HTTP.CLIENT.enforcements.tasks._get_full(uuid=self.uuid)
