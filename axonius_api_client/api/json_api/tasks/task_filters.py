# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import typing as t
import dataclasses

import marshmallow

from ..base2 import BaseModel, BaseSchema
from ..custom_fields import field_from_mm


class TaskFiltersSchema(BaseSchema):
    """Schema for filters for getting enforcement tasks in basic model."""

    action_names = marshmallow.fields.List(
        marshmallow.fields.Str(),
        data_key="action_names",
        description="List of action names to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    discover_cycle_id = marshmallow.fields.List(
        marshmallow.fields.Str(),
        data_key="discover_cycle_id",
        description="List of discovery cycle IDs to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    enforcement_name = marshmallow.fields.List(
        marshmallow.fields.Dict(),
        data_key="enforcement_name",
        description="List of enforcements to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    run = marshmallow.fields.List(
        marshmallow.fields.Int(),
        data_key="run",
        description="List of pretty IDs to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    statuses = marshmallow.fields.List(
        marshmallow.fields.Str(),
        data_key="statuses",
        description="List of statuses to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )

    class Meta:
        """Meta."""

        type_ = "PROTO_TASK_FILTERS"
        unknown = marshmallow.INCLUDE

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return TaskFilters


SCHEMA: marshmallow.Schema = TaskFiltersSchema()


@dataclasses.dataclass
class TaskFilters(BaseModel):
    """Model for filters for getting enforcement tasks in basic model."""

    action_names: t.List[str] = field_from_mm(SCHEMA, "action_names")
    discover_cycle_id: t.List[str] = field_from_mm(SCHEMA, "discover_cycle_id")
    enforcement_name: t.List[dict] = field_from_mm(SCHEMA, "enforcement_name")
    run: t.List[int] = field_from_mm(SCHEMA, "run")
    statuses: t.List[str] = field_from_mm(SCHEMA, "statuses")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    """
    delta 22 milliseconds
    
    duration_filter: DurationOperator
    date_from: t.Optional[datetime.datetime]
        --start-date "2019-01-01T00:00:00Z"
        --start-date "delta:22ms"
        (days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
                            
    date_to: t.Optional[datetime.datetime]
    task_id: t.Optional[str]
    
    dateutil.parser
    enums:
        statuses_filter: t.List[str]
            List of task status to filter by
        action_names: t.List[str]
            List of action names to filter by
        enforcement_ids: t.List[str]
            List of task enforcement ids to filter by
        aggregated_status: t.List[str]
            List of task results to filter by
        discovery_cycle: t.List[str]
            List of  discovery ids to filter by
              - the discovery cycle id isa bson.ObjectId,
                so we can get the datetime of the cycle by:
    bson.ObjectId(discovery_cycle_id).generation_time.replace(tzinfo=dateutil.tz.tzutc())
                
                
        
    """

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return TaskFiltersSchema
