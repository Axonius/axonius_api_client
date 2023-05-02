# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import re
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ....constants.ctypes import PatternLikeListy
from ....exceptions import ApiError, NotFoundError
from ....parsers.tables import tablize
from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm


class AdapterFetchHistoryFiltersSchema(BaseSchemaJson):
    """Schema for fetch history filters response."""

    adapters_filter = mm_fields.List(mm_fields.Dict(), load_default=list, dump_default=list)
    clients_filter = mm_fields.List(mm_fields.Str(), load_default=list, dump_default=list)
    connection_labels_filter = mm_fields.List(mm_fields.Str(), load_default=list, dump_default=list)
    instance_filter = mm_fields.List(mm_fields.Str(), load_default=list, dump_default=list)
    statuses_filter = mm_fields.List(mm_fields.Str(), load_default=list, dump_default=list)
    discoveries_filter = mm_fields.List(mm_fields.Str(), load_default=list, dump_default=list)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AdapterFetchHistoryFilters

    class Meta:
        """JSONAPI config."""

        type_ = "history_filters_response_schema"


SCHEMA = AdapterFetchHistoryFiltersSchema()


@dataclasses.dataclass
class AdapterFetchHistoryFilters(BaseModel):
    """Model for fetch history filters response."""

    adapters_filter: t.List[dict] = field_from_mm(SCHEMA, "adapters_filter")
    clients_filter: t.List[str] = field_from_mm(SCHEMA, "clients_filter")
    connection_labels_filter: t.List[str] = field_from_mm(SCHEMA, "connection_labels_filter")
    instance_filter: t.List[str] = field_from_mm(SCHEMA, "instance_filter")
    statuses_filter: t.List[str] = field_from_mm(SCHEMA, "statuses_filter")
    discoveries_filter: t.List[str] = field_from_mm(SCHEMA, "discoveries_filter")

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AdapterFetchHistoryFiltersSchema

    def check_value(self, value_type: str, value: t.Optional[PatternLikeListy]) -> t.List[str]:
        """Pass."""

        def is_match(value_check):
            """Pass."""
            if isinstance(check, str) and value_check == check:
                return True
            if isinstance(check, t.Pattern) and check.search(value_check):
                return True
            return False

        def check_match(check_value):
            """Pass."""
            if isinstance(check_value, dict):
                for i in check_value.values():
                    if is_match(i):
                        return True
            elif isinstance(check_value, str):
                if is_match(item):
                    return True
            return False

        value_type = self.check_value_type(value_type=value_type)

        if isinstance(value, (list, tuple)):
            ret = []
            for x in value:
                ret += self.check_value(value_type=value_type, value=x)
            return ret
        elif isinstance(value, str):
            check = value.strip()
            if check.startswith("~"):
                check = re.compile(check[1:])
        elif isinstance(value, t.Pattern):
            check = value
        elif value is None:
            return []
        else:
            raise ApiError(
                f"Value must be {PatternLikeListy}, not type={type(value)}, value={value!r}"
            )

        items = getattr(self, value_type)
        matches = []
        valids = []

        if isinstance(items, dict):
            for k, v in items.items():
                valids.append(v)
                if check_match(v):
                    matches.append(k)
        elif isinstance(items, list):
            for item in items:
                valids.append({f"Valid {value_type}": item})
                if check_match(item):
                    matches.append(item)
        else:
            raise ApiError(f"Unexpected type for {value_type} type={type(items)}, value={items!r}")

        if matches:
            return matches

        err = f"No {value_type} matching {value!r} using {check!r} found out of {len(valids)} items"
        err_table = tablize(value=valids, err=err)
        raise NotFoundError(err_table)

    def check_value_type(self, value_type: str) -> str:
        """Pass."""
        value_types = self.value_types()
        if value_type not in value_types:
            valids = ", ".join(value_types)
            raise ApiError(f"Invalid value_type {value_type!r}, valids: {valids}")
        return value_type

    @staticmethod
    def value_types() -> t.List[str]:
        """Pass."""
        return ["adapters", "clients", "connection_labels", "instances", "statuses", "discoveries"]

    @property
    def adapters(self) -> dict:
        """Pass."""
        return {
            x["id"]: {"name": self._get_aname(x["id"]), "name_raw": x["id"], "title": x["name"]}
            for x in self.adapters_filter
        }

    @property
    def clients(self) -> t.List[str]:
        """Pass."""
        return self.clients_filter

    @property
    def connection_labels(self) -> t.List[str]:
        """Pass."""
        return self.connection_labels_filter

    @property
    def instances(self) -> t.List[str]:
        """Pass."""
        return self.instance_filter

    @property
    def statuses(self) -> t.List[str]:
        """Pass."""
        return self.statuses_filter

    @property
    def discoveries(self) -> t.List[str]:
        """Pass."""
        return self.discoveries_filter

    def __str__(self):
        """Pass."""
        items = [
            f"adapters: {len(self.adapters)}",
            f"clients: {len(self.clients)}",
            f"connection_labels: {len(self.connection_labels)}",
            f"instances: {len(self.instances)}",
            f"statuses: {len(self.statuses)}",
            f"discoveries: {len(self.discoveries)}",
        ]
        return ", ".join(items)

    def __repr__(self):
        """Pass."""
        return self.__str__()
