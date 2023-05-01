# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm
from .adapter_node import AdapterNode


class AdapterSchema(BaseSchemaJson):
    """Schema for adapters data response."""

    adapters_data = mm_fields.List(mm_fields.Dict())

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return Adapter

    class Meta:
        """JSONAPI config."""

        type_ = "adapters_schema"


SCHEMA = AdapterSchema()


@dataclasses.dataclass
class Adapter(BaseModel):
    """Model for adapters data response."""

    adapters_data: t.List[dict] = field_from_mm(SCHEMA, "adapters_data")
    id: str = field_from_mm(SCHEMA, "id")

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    _adapter_nodes: t.ClassVar[t.List["AdapterNode"]] = None
    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    def __post_init__(self):
        """Pass."""
        self.adapter_name_raw = self.id
        self.adapter_name = self._get_aname(self.id)
        self.document_meta = self.document_meta.pop(self.id, None)
        """
        document_meta: {}
            config: {} - adapter advanced settings
                ActiveDirectoryAdapter: {} - adapter specific advanced settings
                    config: {} - current config
                    schema: {} - schema for config
                AdapterBase: {} - adapter generic advanced settings
                    config: {} - current config
                    schema: {} - schema for config
                DiscoverySchema: {} - adapter discovery advanced settings
                    config: {} - current config
                    schema: {} - schema for config
            schema: {} - adapter connection schema
            clients_schema: {} - adapter connection special schemas
                settings: {} - for 'connect_via_tunnel' - will ignore for now
                connectionDiscoverySchema: {} - schema for connection specific discovery settings
        """

    @property
    def adapter_nodes(self) -> t.List[AdapterNode]:
        """Pass."""

        def load(data):
            """Pass."""
            extra_attributes = {k: data.pop(k) for k in list(data) if k not in fields_known}
            loaded = schema.load(data, unknown=marshmallow.INCLUDE)
            loaded.Adapter = self
            # noinspection PyUnresolvedReferences
            loaded.HTTP = self.HTTP
            loaded.extra_attributes = extra_attributes
            return loaded

        if not isinstance(self._adapter_nodes, list):
            fields_known = [x.name for x in dataclasses.fields(AdapterNode)]
            schema = AdapterNode.schema()
            self._adapter_nodes = [load(x) for x in self.adapters_data]

        return self._adapter_nodes

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AdapterSchema

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return ["adapter_name", "adapter_nodes"]
