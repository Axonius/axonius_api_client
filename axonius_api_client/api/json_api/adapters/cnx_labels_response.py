# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ..generic import Metadata, MetadataSchema


class CnxLabelsSchema(MetadataSchema):
    """Schema for response to get connection labels."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CnxLabels

    class Meta:
        """JSONAPI config."""

        type_ = "metadata_schema"


@dataclasses.dataclass
class CnxLabels(Metadata):
    """Model for response to get connection labels."""

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return CnxLabelsSchema

    @property
    def labels(self) -> t.List[dict]:
        """Pass."""
        return self.document_meta.get("labels") or []

    @property
    def label_values(self) -> t.List[str]:
        """Pass."""
        return list(set([x["label"] for x in self.labels]))

    def get_label(
        self,
        client_id: str,
        adapter_name_raw: t.Optional[str] = None,
        node_id: t.Optional[str] = None,
    ) -> str:
        """Pass."""
        for label in self.labels:
            if client_id != label["client_id"]:
                continue

            if isinstance(adapter_name_raw, str) and adapter_name_raw != label["plugin_name"]:
                continue

            if isinstance(node_id, str) and node_id != label["node_id"]:
                continue
            return label["label"]
        return ""
