# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow

from ....parsers.config import parse_schema
from ....tools import listify
from ..base import BaseModel
from ..custom_fields import SchemaDatetime, dump_date, get_field_dc_mm
from .cnx_labels_response import CnxLabels


@dataclasses.dataclass(repr=False)
class Cnx(BaseModel):
    """Manually defined container for a connection."""

    adapter_name: str
    client_id: str
    uuid: str
    node_id: str
    node_name: str
    status: str

    active: bool = False
    client_config: t.Optional[dict] = dataclasses.field(default_factory=dict)
    connection_discovery: t.Optional[dict] = dataclasses.field(default_factory=dict)
    connection_advanced_config: t.Optional[dict] = dataclasses.field(default_factory=dict)
    date_fetched: t.Optional[str] = None
    last_fetch_time: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    error: t.Optional[str] = ""
    tunnel_id: t.Optional[str] = None
    failed_connections_limit_exceeded: t.Optional[int] = None
    adapter_name_raw: t.ClassVar[str] = None
    connection_label: t.ClassVar[str] = None
    note: t.Optional[t.Any] = None

    PARENT: t.ClassVar["Cnxs"] = None
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        self.adapter_name_raw = self.adapter_name
        self.adapter_name = self._get_aname(self.adapter_name)

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return [
            "adapter_name",
            "client_id",
            "uuid",
            "node_id",
            "node_name",
            "status",
            "error",
        ]

    def __repr__(self):
        """Pass."""
        return self.__str__()

    @property
    def working(self) -> bool:
        """Pass."""
        return self.status == "success" and not self.error

    def to_dict_old(self) -> dict:
        """Pass."""
        ret = {
            "active": self.active,
            "adapter_name": self.adapter_name,
            "adapter_name_raw": self.adapter_name_raw,
            "id": self.client_id,
            "uuid": self.uuid,
            "node_id": self.node_id,
            "node_name": self.node_name,
            "status": self.status,
            "config": self.client_config,
            "config_discovery": self.connection_discovery,
            "date_fetched": self.date_fetched,
            "last_fetched_time": dump_date(self.last_fetch_time),
            "working": self.working,
            "error": self.error,
            "tunnel_id": self.tunnel_id,
            "schemas": self.PARENT.schema_cnx,
            "schema_discovery": self.PARENT.schema_discovery,
            "connection_label": self.connection_label,
        }
        return ret

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


CNX_SCHEMA = Cnx.schema()


@dataclasses.dataclass
class Cnxs(BaseModel):
    """Manual model to extract the JSONAPI due to oddities."""

    cnxs: t.List[Cnx]
    meta: dict
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    _get_labels: t.ClassVar[t.Optional[CnxLabels]] = None

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None

    @classmethod
    def load_response(cls, data: dict, **kwargs):
        """Pass."""
        http = kwargs["http"]

        def load_cnx(value):
            """Pass."""
            data_attrs = value.get("attributes")
            obj_new = None
            if data_attrs:
                extra_attributes = {
                    k: data_attrs.pop(k) for k in list(data_attrs) if k not in fields_known
                }
                obj_new = CNX_SCHEMA.load(data_attrs, unknown=marshmallow.INCLUDE)
                obj_new.extra_attributes = extra_attributes
            return obj_new

        fields_known = [x.name for x in dataclasses.fields(Cnx)]

        meta = data["meta"]
        cnxs_raw = listify(data["data"])
        cnxs = [y for y in [load_cnx(x) for x in cnxs_raw] if y]

        loaded = cls(cnxs=cnxs, meta=meta)
        loaded.HTTP = http
        labels = loaded.get_labels()

        for cnx in loaded.cnxs:
            cnx.PARENT = loaded
            cnx.HTTP = loaded.HTTP
            cnx.connection_label = labels.get_label(
                adapter_name_raw=cnx.adapter_name_raw, node_id=cnx.node_id, client_id=cnx.client_id
            )

        return loaded

    @property
    def schema_discovery(self) -> dict:
        """Pass."""
        return parse_schema(self.meta["connectionDiscoverySchema"])

    @property
    def schema_cnx(self) -> dict:
        """Pass."""
        return parse_schema(self.meta["schema"])

    def get_labels(self, cached: bool = False) -> CnxLabels:
        """Pass."""
        if not cached or not getattr(self, "_get_labels", None):
            # noinspection PyUnresolvedReferences,PyProtectedMember
            self._get_labels = self.HTTP.CLIENT.adapters.cnx._get_labels()

        return getattr(self, "_get_labels")
