# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi

from ...exceptions import ApiError
from ...tools import csv_writer, is_str
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm
from .nested_access import Access, AccessMode, AccessSchemaJson
from .saved_queries import SavedQuery
from .spaces_export import SpacesExport


class ExportableSpacesResponseSchema(BaseSchemaJson):
    """Pass."""

    spaces = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(), load_default=[], dump_default=[]
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ExportableSpacesResponse

    class Meta:
        """Pass."""

        type_ = "export_permitted_spaces_schema"


@dataclasses.dataclass
class ExportableSpacesResponse(BaseModel):
    """Pass."""

    spaces: t.List[str] = get_field_dc_mm(
        mm_field=ExportableSpacesResponseSchema._declared_fields["spaces"], default_factory=list
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ExportableSpacesResponseSchema


class ExportSpacesRequestSchema(BaseSchemaJson):
    """Pass."""

    spaces = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        load_default=[],
        dump_default=[],
        description="Spaces names to export",
    )
    as_template = SchemaBool(
        load_default=False, dump_default=False, description="Should this export return a template"
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ExportSpacesRequest

    class Meta:
        """Pass."""

        type_ = "export_spaces_schema"


@dataclasses.dataclass
class ExportSpacesRequest(BaseModel):
    """Pass."""

    spaces: t.List[str] = get_field_dc_mm(
        mm_field=ExportSpacesRequestSchema._declared_fields["spaces"], default_factory=list
    )
    as_template: bool = get_field_dc_mm(
        mm_field=ExportSpacesRequestSchema._declared_fields["as_template"], default=False
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ExportSpacesRequestSchema


class ImportSpacesRequestSchema(BaseSchemaJson):
    """Pass."""

    data = marshmallow_jsonapi.fields.Dict(description="The spaces data returned from an export")
    replace = SchemaBool(
        load_default=False,
        dump_default=False,
        description="If true, existing charts and saved queries will be overwritten",
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ImportSpacesRequest

    class Meta:
        """Pass."""

        type_ = "import_spaces_schema"


@dataclasses.dataclass
class ImportSpacesRequest(BaseModel):
    """Pass."""

    data: dict = get_field_dc_mm(mm_field=ImportSpacesRequestSchema._declared_fields["data"])
    replace: bool = get_field_dc_mm(
        mm_field=ImportSpacesRequestSchema._declared_fields["replace"], default=False
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ImportSpacesRequestSchema


class ImportSpacesResponseSchema(BaseSchema):
    """Pass."""

    inserted_spaces = marshmallow_jsonapi.fields.Integer(
        description="Number of inserted spaces.", load_default=0, dump_default=0
    )
    replaced_spaces = marshmallow_jsonapi.fields.Integer(
        description="Number of replaced spaces.", load_default=0, dump_default=0
    )
    inserted_charts = marshmallow_jsonapi.fields.Integer(
        description="Number of inserted charts.", load_default=0, dump_default=0
    )
    replaced_charts = marshmallow_jsonapi.fields.Integer(
        description="Number of replaced charts.", load_default=0, dump_default=0
    )
    inserted_queries = marshmallow_jsonapi.fields.Integer(
        description="Number of inserted saved queries.", load_default=0, dump_default=0
    )
    replaced_queries = marshmallow_jsonapi.fields.Integer(
        description="Number of replaced saved queries.", load_default=0, dump_default=0
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ImportSpacesResponse

    class Meta:
        """Pass."""

        type_ = "import_spaces_schema"


@dataclasses.dataclass
class ImportSpacesResponse(BaseModel):
    """Pass."""

    inserted_spaces: int = get_field_dc_mm(
        mm_field=ImportSpacesResponseSchema._declared_fields["inserted_spaces"], default=0
    )
    replaced_spaces: int = get_field_dc_mm(
        mm_field=ImportSpacesResponseSchema._declared_fields["replaced_spaces"], default=0
    )
    inserted_charts: int = get_field_dc_mm(
        mm_field=ImportSpacesResponseSchema._declared_fields["inserted_charts"], default=0
    )
    replaced_charts: int = get_field_dc_mm(
        mm_field=ImportSpacesResponseSchema._declared_fields["replaced_charts"], default=0
    )
    inserted_queries: int = get_field_dc_mm(
        mm_field=ImportSpacesResponseSchema._declared_fields["inserted_queries"], default=0
    )
    replaced_queries: int = get_field_dc_mm(
        mm_field=ImportSpacesResponseSchema._declared_fields["replaced_queries"], default=0
    )

    spaces_export: t.ClassVar[t.Optional[SpacesExport]] = None
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ImportSpacesResponseSchema

    def __str__(self) -> str:
        """Pass."""
        data = self.to_dict()
        items = []
        if isinstance(self.spaces_export, SpacesExport):
            items += self.spaces_export.to_str(queries=False, chart_queries=False)

        items += ["", "*" * 80, "Spaces Import Report", *[f"  - {k}: {v}" for k, v in data.items()]]
        return "\n".join(items)

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


class SizeSchema(BaseSchema):
    """Pass."""

    column = marshmallow_jsonapi.fields.Int()
    row = marshmallow_jsonapi.fields.Int()

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Size


class ChartSchema(BaseSchema):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    description = marshmallow_jsonapi.fields.Str(allow_none=True)
    metric = marshmallow_jsonapi.fields.Str()
    space = marshmallow_jsonapi.fields.Str()
    user_id = marshmallow_jsonapi.fields.Str()
    id = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    view = marshmallow_jsonapi.fields.Str()
    config = marshmallow_jsonapi.fields.Dict()
    adapter_categories = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Int(), allow_none=True, load_default=None, dump_default=None
    )  # ??
    used_adapters = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Int(), allow_none=True, load_default=None, dump_default=None
    )  # ??
    last_updated = SchemaDatetime(allow_none=True)
    size = marshmallow.fields.Nested(SizeSchema)
    private = SchemaBool(allow_none=True, load_default=False, dump_default=False)
    shared = SchemaBool(allow_none=True, load_default=None, dump_default=False)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Chart


class SpacesDetailsSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(description="The name of the space")
    description = marshmallow_jsonapi.fields.Str(
        description="space description", load_default="", dump_default="", allow_none=True
    )
    user_interests = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Int(),
        description="A list of the relevant user interests of the space",
    )
    adapter_categories = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Int(),
        description="A list of the Relevant adapter categories ids (predefined adapter categories)",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    access = marshmallow_jsonapi.fields.Nested(
        AccessSchemaJson,
        load_default=Access().to_dict(),
        dump_default=Access().to_dict(),
    )
    uuid = marshmallow_jsonapi.fields.Str(description="The DB id of the space")
    public = marshmallow_jsonapi.fields.Bool(
        description="Whether the space is public or restricted",
    )
    roles = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(
            description="The list of role ids allowed to access the space"
        )
    )
    type = marshmallow_jsonapi.fields.Str(
        description="The type of the space from: default, personal, custom"
    )
    initiated = marshmallow_jsonapi.fields.Bool(
        description="Has this space been initiated (The user selected an"
        " empty space or chose a template)",
        missing=False,
    )
    origin = marshmallow_jsonapi.fields.Str(
        description="The origin of the space from: empty, template", allow_none=True
    )
    spaceFilter = marshmallow_jsonapi.fields.Dict(
        description="The space filter object to filter the space data", allow_none=True
    )
    last_updated = SchemaDatetime(
        allow_none=True,
        description="The last time this space charts was updated",
    )
    created_by = marshmallow_jsonapi.fields.Str(
        description="user that created", load_default=None, dump_default=None, allow_none=True
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SpacesDetails

    class Meta:
        """Pass."""

        type_ = "spaces_details_schema"  # Required
        self_url = "/api/dashboard/{id}"
        self_url_kwargs = {"id": "<id>"}
        self_url_many = "/api/dashboard/"


class SpaceChartsSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(description="The name of the space")
    description = marshmallow_jsonapi.fields.Str(
        description="space description", load_default="", dump_default="", allow_none=True
    )
    user_interests = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Int(),
        description="A list of the relevant user interests of the space",
    )
    adapter_categories = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Int(),
        description="A list of the Relevant adapter categories ids (predefined adapter categories)",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    access = marshmallow_jsonapi.fields.Nested(
        AccessSchemaJson,
        load_default=Access().to_dict(),
        dump_default=Access().to_dict(),
    )
    uuid = marshmallow_jsonapi.fields.Str(description="The DB id of the space")
    public = marshmallow_jsonapi.fields.Bool(
        description="Whether the space is public or restricted",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    roles = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(
            description="The list of role ids allowed to access the space"
        )
    )
    type = marshmallow_jsonapi.fields.Str(
        description="The type of the space from: default, personal, custom"
    )
    initiated = marshmallow_jsonapi.fields.Bool(
        description="Has this space been initiated (The user selected an"
        " empty space or chose a template)",
        missing=False,
    )
    origin = marshmallow_jsonapi.fields.Str(
        description="The origin of the space from: empty, template", allow_none=True
    )
    spaceFilter = marshmallow_jsonapi.fields.Dict(
        description="The space filter object to filter the space data", allow_none=True
    )
    last_updated = SchemaDatetime(
        allow_none=True,
        description="The last time this space charts was updated",
    )
    panels_order = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(
            description="The list of charts ids of the space, in the order of presentation"
        )
    )
    charts = marshmallow_jsonapi.fields.List(
        marshmallow.fields.Dict(),
        description="The list of chart configurations of the space",
    )
    created_by = marshmallow_jsonapi.fields.Str(
        description="user that created", load_default=None, dump_default=None, allow_none=True
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SpaceCharts

    class Meta:
        """Pass."""

        type_ = "space_charts_schema"  # Required


@dataclasses.dataclass
class Size(BaseModel):
    """Pass."""

    column: int
    row: int

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SizeSchema

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return [
            "column",
            "row",
        ]

    @staticmethod
    def _str_join() -> str:
        """Pass."""
        return ", "

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


@dataclasses.dataclass
class ChartQuery(BaseModel):
    """Pass."""

    query: SavedQuery
    purpose: str = ""

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"name={self.query.name!r}",
            f"module={self.query.module!r}",
            f"purpose={self.purpose!r}",
        ]
        return "ChartQuery(" + ", ".join(items) + ")"

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


@dataclasses.dataclass
class Chart(BaseModel):
    """Pass."""

    name: str
    metric: str
    space: str
    user_id: str
    id: str
    uuid: str
    view: str
    config: dict
    size: Size
    private: t.Optional[bool] = False
    shared: t.Optional[bool] = None
    description: t.Optional[str] = None
    adapter_categories: t.Optional[t.List[int]] = None
    used_adapters: t.Optional[t.List[str]] = None
    last_updated: t.Optional[datetime.datetime] = None

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ChartSchema

    @property
    def config_view(self) -> t.Optional[str]:
        """Pass."""
        return self.config.get("view")

    @property
    def config_selected_view(self) -> t.Optional[str]:
        """Pass."""
        return self.config.get("selected_view")

    @property
    def config_base_view(self) -> t.Optional[str]:
        """Pass."""
        return self.config.get("base")

    @property
    def config_intersecting_views(self) -> t.Optional[t.List[str]]:
        """Pass."""
        return self.config.get("intersecting")

    @property
    def config_views(self) -> t.Optional[t.List[dict]]:
        """Pass."""
        return self.config.get("views")

    @property
    def config_module(self) -> t.Optional[str]:
        """Pass."""
        return self.config.get("entity")

    @property
    def config_modules(self) -> t.List[str]:
        """Pass."""
        return (
            list(
                set(
                    [
                        x.get("entity")
                        for x in self.config_views
                        if isinstance(x, dict) and isinstance(x.get("entity"), str)
                    ]
                )
            )
            if isinstance(self.config_views, list)
            else []
        )

    def get_query(self, module: str, value: str, purpose: str) -> ChartQuery:
        """Pass."""
        apiobj = getattr(self.SPACE.HTTP.CLIENT, module)
        query = apiobj.saved_query.get_by_multi(sq=value, as_dataclass=True, cache=True)
        return ChartQuery(query=query, purpose=purpose)

    @property
    def export_unsupported_metrics(self) -> t.List[str]:
        """Pass."""
        return [
            "intersect",
            "compare",
            "summary",
            "matrix",
        ]

    def export_to_csv(self, error: bool = True):
        """Pass."""
        if self.metric in self.export_unsupported_metrics:
            err = f"Charts using a metric of {self.metric!r} do not support export to CSV"
            if error:
                raise ApiError(err)

            ret = csv_writer(rows=[{"export_chart_csv_error": err, "chart": str(self)}])
        else:
            try:
                ret = self.SPACE.HTTP.CLIENT.dashboard_spaces._export_chart_csv(uuid=self.uuid)
            except Exception as exc:
                if error:
                    raise

                err = f"Export to CSV Failed:\n{exc}"
                ret = csv_writer(rows=[{"export_chart_csv_error": err, "chart": str(self)}])
        return ret

    @property
    def queries(self) -> t.List[ChartQuery]:
        """Pass."""
        ret = []

        if is_str(self.config_module):
            if is_str(self.config_view):
                ret.append(
                    self.get_query(
                        module=self.config_module, value=self.config_view, purpose="query"
                    )
                )

            if is_str(self.config_selected_view):
                ret.append(
                    self.get_query(
                        module=self.config_module, value=self.config_selected_view, purpose="query"
                    )
                )

            if is_str(self.config_base_view):
                ret.append(
                    self.get_query(
                        module=self.config_module, value=self.config_base_view, purpose="base"
                    )
                )

            if isinstance(self.config_intersecting_views, list):
                ret += [
                    self.get_query(module=self.config_module, value=x, purpose="intersect")
                    for x in self.config_intersecting_views
                ]

        if isinstance(self.config_views, list):
            ret += [
                self.get_query(module=x["entity"], value=x["id"], purpose="queries")
                for x in self.config_views
                if isinstance(x, dict) and is_str(x.get("entity")) and is_str(x.get("id"))
            ]
        return ret

    @property
    def queries_str(self) -> t.List[str]:
        """Pass."""
        return [f"{x}" for x in self.queries]

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return [
            "name",
            "description",
            "uuid",
            "metric",
            "view",
            "size",
            "last_updated",
            "queries",
        ]

    @staticmethod
    def _str_join() -> str:
        """Pass."""
        return ", "

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


@dataclasses.dataclass
class SpacesDetails(BaseModel):
    """Pass."""

    id: str
    name: str = get_field_dc_mm(mm_field=SpacesDetailsSchema._declared_fields["name"])
    uuid: str = get_field_dc_mm(mm_field=SpacesDetailsSchema._declared_fields["name"])
    type: str = get_field_dc_mm(mm_field=SpacesDetailsSchema._declared_fields["type"])
    public: t.Optional[bool] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["public"], default=None
    )
    description: t.Optional[str] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["description"], default=""
    )
    origin: t.Optional[str] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["origin"], default=None
    )
    roles: t.List[str] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["roles"], default_factory=list
    )
    user_interests: t.List[int] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["user_interests"], default_factory=list
    )
    adapter_categories: t.List[int] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["adapter_categories"], default_factory=list
    )
    initiated: bool = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["initiated"], default=False
    )
    spaceFilter: t.Optional[dict] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["spaceFilter"], default=None
    )
    last_updated: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["last_updated"], default=None
    )
    access: t.Optional[Access] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["access"], default_factory=Access
    )
    created_by: t.Optional[str] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["created_by"], default=None
    )

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SpacesDetailsSchema


@dataclasses.dataclass
class SpaceCharts(BaseModel):
    """Pass."""

    id: str
    name: str = get_field_dc_mm(mm_field=SpacesDetailsSchema._declared_fields["name"])
    uuid: str = get_field_dc_mm(mm_field=SpacesDetailsSchema._declared_fields["name"])
    type: str = get_field_dc_mm(mm_field=SpacesDetailsSchema._declared_fields["type"])
    public: t.Optional[bool] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["public"], default=None
    )
    description: t.Optional[str] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["description"], default=""
    )
    origin: t.Optional[str] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["origin"], default=None
    )
    roles: t.List[str] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["roles"], default_factory=list
    )
    user_interests: t.List[int] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["user_interests"], default_factory=list
    )
    adapter_categories: t.Optional[t.List[int]] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["adapter_categories"], default_factory=list
    )
    initiated: bool = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["initiated"], default=False
    )
    spaceFilter: t.Optional[dict] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["spaceFilter"], default=None
    )
    last_updated: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["last_updated"], default=None
    )
    access: t.Optional[Access] = get_field_dc_mm(
        mm_field=SpacesDetailsSchema._declared_fields["access"], default_factory=Access
    )
    panels_order: t.List[str] = get_field_dc_mm(
        mm_field=SpaceChartsSchema._declared_fields["panels_order"], default_factory=list
    )
    charts: t.List[dict] = get_field_dc_mm(
        mm_field=SpaceChartsSchema._declared_fields["charts"], default_factory=list
    )
    created_by: t.Optional[str] = get_field_dc_mm(
        mm_field=SpaceChartsSchema._declared_fields["created_by"], default=None
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        if not isinstance(self.public, bool):
            self.public = self.access.mode == AccessMode.public.value

        fields_known: t.List[str] = [x.name for x in dataclasses.fields(Chart)]
        schema: marshmallow.Schema = ChartSchema(many=False, unknown=marshmallow.INCLUDE)

        def load(data: dict) -> Chart:
            extra_attributes: dict = {k: data.pop(k) for k in list(data) if k not in fields_known}
            loaded: Chart = schema.load(data, unknown=marshmallow.INCLUDE)
            loaded.SPACE = self
            loaded.extra_attributes = extra_attributes
            return loaded

        self.charts: t.List[Chart] = [load(x) for x in self.charts]

    @property
    def charts_by_order(self) -> t.List[Chart]:
        """Pass."""
        charts_by_uuid = {x.uuid: x for x in self.charts}
        return [charts_by_uuid[x] for x in self.panels_order]

    @property
    def chart_names(self) -> t.List[str]:
        """Pass."""
        return [x.name for x in self.charts_by_order]

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SpaceChartsSchema

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return [
            "name",
            "uuid",
            "type",
            "description",
            "last_updated",
            "access",
            "public",
            "chart_names",
        ]

    @staticmethod
    def _str_join() -> str:
        """Pass."""
        return ", "
